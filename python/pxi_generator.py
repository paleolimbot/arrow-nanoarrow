# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import io
import tokenize
import textwrap


class Content:

    def __init__(self, content, indent=0) -> None:
        self._indent = indent
        self._content = self._unindent(content, indent)

    def render(self, out):
        docstring = self.find_docstring()

        # Only render if this is documented
        if not docstring:
            return

        out_tokens = []
        for tok_type, tok_val, _, _, _ in self.tokens():
            # Skip any comments
            if tok_type == tokenize.COMMENT:
                continue

            # Append the token
            out_tokens.append((tok_type, tok_val))

            # We only need until the actual indent happens
            if tok_type == tokenize.INDENT:
                break

        # Because of the next loop, put a dummy token at the end
        out_tokens.append((tokenize.NAME, "..."))

        # One more pass to transform `cdef class` -> `class` and
        # `Type param` -> `param: Type`
        out_tokens_trans = []
        for i in range(0, len(out_tokens) - 1):
            tok_type0, tok_val0 = out_tokens[i]
            tok_type, tok_val = out_tokens[i + 1]

            if tok_type0 == tokenize.NAME and tok_type == tokenize.NAME:
                if tok_val0 == "cdef" and tok_val == "class":
                    # cdef class -> class
                    continue

                elif tok_val0 in ("def", "class"):
                    #
                    out_tokens_trans.append((tok_type0, tok_val0))
                else:
                    out_tokens_trans.extend(
                        [
                            (tokenize.NAME, tok_val),
                            (tokenize.OP, ":"),
                            (tokenize.NAME, tok_val0),
                        ]
                    )
            else:
                out_tokens_trans.append((tok_type0, tok_val0))

        # Add the docstring and render
        out_tokens_trans.append((tokenize.STRING, docstring))
        out_str = tokenize.untokenize(out_tokens_trans)
        out.write(textwrap.indent(out_str, " " * self._indent))
        out.write("\n\n")

        # Render children
        for child in self.children():
            child.render(out)

    def children(self, initial_level=-1):
        for start, end in self._child_blocks(initial_level):
            start_pos = self._row_col_to_offset(start.start)
            end_pos = self._row_col_to_offset(end.end)

            start_indent = start.start[1]
            start_indent_str = " " * start_indent
            yield Content(
                start_indent_str + self._content[start_pos:end_pos], start_indent
            )

    def find_docstring(self):
        tok = self._find_next_docstring()
        if tok is not None:
            return tok.string
        else:
            return None

    def _child_blocks(self, initial_level=-1):
        level = initial_level
        def_start = None
        for tok in self.tokens():
            if tok.type in (tokenize.COMMENT, tokenize.NL):
                continue

            # Save the start of the def/class (hopefully skipping variable definitions)
            if (
                level == 0
                and tok.type == tokenize.NAME
                and tok.string in ("def", "cdef", "cpdef", "class")
                and (def_start is None or def_start.line != tok.line)
            ):
                def_start = tok

            # Keep track of indentation level and stop iterating when we get back
            # to a zero indentation level
            if tok.type == tokenize.INDENT:
                level += 1
            elif tok.type == tokenize.DEDENT:
                level -= 1
                if level == 0:
                    yield def_start, tok

    # The tokenizer gives us row/col, but we need the offset into the string
    def _row_col_to_offset(self, row_and_col):
        f = io.StringIO(self._content)
        row, col = row_and_col
        for _ in range(row - 1):
            f.readline()
        return f.tell() + col

    def _find_next_docstring(self):
        found_indent = False
        for tok in self.tokens():
            if tok.type in (tokenize.COMMENT, tokenize.NL):
                continue

            if not found_indent and tok.type == tokenize.INDENT:
                found_indent = True
                continue

            if found_indent and tok.type == tokenize.STRING:
                break

        return tok

    def tokens(self):
        return tokenize.generate_tokens(io.StringIO(self._content).readline)

    def _unindent(self, content, n_spaces):
        if n_spaces == 0:
            return content

        indent_str = " " * n_spaces
        out_str = io.StringIO()
        in_str = io.StringIO(content)
        for line in in_str:
            # Blank lines are OK; improperly indented comments
            # may throw an error here
            if line.strip() == "":
                out_str.write(line)
            elif line[:n_spaces] == indent_str:
                out_str.write(line[n_spaces:])
            else:
                raise ValueError(f"line '{line}' is not indented by {n_spaces} spaces")

        return out_str.getvalue()


import io

f = Content(
    """
cdef class Foo:
    \"\"\"This is a class docstring\"\"\"

    # This is a comment
    def some_function(CythonType param1, param2: PythonType) -> OutTypeHint:
        \"\"\"This is a docstring

        ...which contains content we'd like in the pyi file.
        \"\"\"
        print("this is a function")

"""
)

out = io.StringIO()
f.render(out)
print(out.getvalue())
