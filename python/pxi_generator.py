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


class Content:

    def __init__(self, content, indent=0) -> None:
        self._indent = indent
        self._content = self._unindent(content, indent)

    def children(self):
        for start, end in self._child_blocks():
            start_pos = self._row_col_to_offset(start.start)
            end_pos = self._row_col_to_offset(end.end)

            start_indent = start.start[1]
            yield Content(self._content[start_pos:end_pos], start_indent)

    def _child_blocks(self):
        level = 0
        def_start = None
        for tok in tokenize.generate_tokens(io.StringIO(self._content).readline):
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
        for tok in tokenize.generate_tokens(io.StringIO(self._content).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL):
                continue

            if not found_indent and tok.type == tokenize.INDENT:
                found_indent = True
                continue

            if found_indent and tok.type == tokenize.STRING:
                break

        return tok

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


content = """

# This is a comment
cpdef some_function(CythonType param1, param2: PythonType) -> OutTypeHint:
    \"\"\"This is a docstring

    ...which contains content we'd like in the pyi file.
    \"\"\"
    print("this is a function")


cdef class SomeClass:
    \"\"\"This is the documentation for SomeClass

    Here is a second paragraph
    \"\"\"

    # Another comment that might be anywhere
    def some_method(self, some_param: HintedType, CythonType some_other_param) -> OutType:
        \"\"\"This is a method

        ...that contains a mix of Python-style and Cython-style type hints
        and a docstring.
        \"\"\"
        print("this is a method")

    # A comment that is not properly indented
    def some_other_method(self):
        pass

    @staticmethod
    def a_static_method():
        pass

    @classmethod
    def a_class_method(cls):
        pass


cdef class SomeSubClass(SomeClass):
    \"\"\"This is the documentation for a subclass

    ...we don't need any stubs for superclass methods but we do need

    \"\"\"
    def some_subclass_method(self):
        pass

"""


c = Content(content)
for item in c.children():
    print("-" * 30)
    print(item._content)
    print("-" * 30)
