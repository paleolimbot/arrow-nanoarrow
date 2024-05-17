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

from enum import Enum

def c_version():
    """Return the nanoarrow C library version string"""

class NanoarrowException(RuntimeError):
    """An error resulting from a call to the nanoarrow C library

    Calls to the nanoarrow C library and/or the Arrow C Stream interface
    callbacks return an errno error code and sometimes a message with extra
    detail. This exception wraps a RuntimeError to format a suitable message
    and store the components of the original error.
    """

class Error:
    """Memory holder for an ArrowError

    ArrowError is the C struct that is optionally passed to nanoarrow functions
    when a detailed error message might be returned. This class holds a C
    reference to the object and provides helpers for raising exceptions based
    on the contained message.
    """

    def raise_message(self, what, code):
        """Raise a NanoarrowException from this message"""
    @staticmethod
    def raise_error(what, code):
        """Raise a NanoarrowException without a message"""

class CArrowType:
    """
    Wrapper around ArrowType to provide implementations in Python access
    to the values.

    This could in theory use cpdef enum, but an initial attempt to do so
    resulted Cython duplicating some function definitions. For now, we resort
    to a more manual trampoline of values to make them accessible from
    schema.py.
    """

class CArrowTimeUnit:
    """
    Wrapper around ArrowTimeUnit to provide implementations in Python access
    to the values.
    """

class DeviceType(Enum):
    """
    An enumerator providing access to the device constant values
    defined in the Arrow C Device interface. Unlike the other enum
    accessors, this Python Enum is defined in Cython so that we can use
    the bulit-in functionality to do better printing of device identifiers
    for classes defined in Cython. Unlike the other enums, users don't
    typically need to specify these (but would probably like them printed
    nicely).
    """

class Device:
    """ArrowDevice wrapper

    The ArrowDevice structure is a nanoarrow internal struct (i.e.,
    not ABI stable) that contains callbacks for device operations
    beyond its type and identifier (e.g., copy buffers to or from
    a device).
    """

class CSchema:
    """Low-level ArrowSchema wrapper

    This object is a literal wrapper around a read-only ArrowSchema. It provides field accessors
    that return Python objects and handles the C Data interface lifecycle (i.e., initialized
    ArrowSchema structures are always released).

    See `nanoarrow.c_schema()` for construction and usage examples.
    """

    @staticmethod
    def _import_from_c_capsule(schema_capsule):
        """
        Import from a ArrowSchema PyCapsule

        Parameters
        ----------
        schema_capsule : PyCapsule
            A valid PyCapsule with name 'arrow_schema' containing an
            ArrowSchema pointer.
        """
    def __arrow_c_schema__(self):
        """
        Export to a ArrowSchema PyCapsule
        """
    def _capsule(self):
        """
        Returns the capsule backing this CSchema or None if it does not exist
        or points to a parent ArrowSchema.
        """

class CSchemaView:
    """Low-level ArrowSchemaView wrapper

    This object is a literal wrapper around a read-only ArrowSchemaView. It provides field accessors
    that return Python objects and handles structure lifecycle. Compared to an ArrowSchema,
    the nanoarrow ArrowSchemaView facilitates access to the deserialized content of an ArrowSchema
    (e.g., parameter values for parameterized types).

    See `nanoarrow.c_schema_view()` for construction and usage examples.
    """

    def buffer_format(self):
        """The Python struct format representing an element of this type
        or None if there is no Python format string that can represent this
        type.
        """

class CArray:
    """Low-level ArrowArray wrapper

    This object is a literal wrapper around a read-only ArrowArray. It provides field accessors
    that return Python objects and handles the C Data interface lifecycle (i.e., initialized
    ArrowArray structures are always released).

    See `nanoarrow.c_array()` for construction and usage examples.
    """

    @staticmethod
    def _import_from_c_capsule(schema_capsule, array_capsule):
        """
        Import from a ArrowSchema and ArrowArray PyCapsule tuple.

        Parameters
        ----------
        schema_capsule : PyCapsule
            A valid PyCapsule with name 'arrow_schema' containing an
            ArrowSchema pointer.
        array_capsule : PyCapsule
            A valid PyCapsule with name 'arrow_array' containing an
            ArrowArray pointer.
        """
    def __arrow_c_array__(self, requested_schema=None):
        """
        Get a pair of PyCapsules containing a C ArrowArray representation of the object.

        Parameters
        ----------
        requested_schema : PyCapsule | None
            A PyCapsule containing a C ArrowSchema representation of a requested
            schema. Not supported.

        Returns
        -------
        Tuple[PyCapsule, PyCapsule]
            A pair of PyCapsules containing a C ArrowSchema and ArrowArray,
            respectively.
        """

class CArrayView:
    """Low-level ArrowArrayView wrapper

    This object is a literal wrapper around an ArrowArrayView. It provides field accessors
    that return Python objects and handles the structure lifecycle (i.e., initialized
    ArrowArrayView structures are always released).

    See `nanoarrow.c_array_view()` for construction and usage examples.
    """

class SchemaMetadata:
    """Wrapper for a lazily-parsed CSchema.metadata string"""

class CBufferView:
    """Wrapper for Array buffer content

    This object is a Python wrapper around a buffer held by an Array.
    It implements the Python buffer protocol and is best accessed through
    another implementor (e.g., `np.array(array_view.buffers[1])`)). Note that
    this buffer content does not apply any parent offset.
    """

class CBuffer:
    """Wrapper around readable owned buffer content

    Like the CBufferView, the CBuffer represents readable buffer content; however,
    unlike the CBufferView, the CBuffer always represents a valid ArrowBuffer C object.
    """

class CBufferBuilder:
    """Wrapper around writable CPU buffer content

    This class provides a growable type-aware buffer that can be used
    to create a typed buffer from a Python iterable. This method of
    creating a buffer is usually slower than constructors like
    ``array.array()`` or ``numpy.array()``; however, this class supports
    all Arrow types with a single data buffer (e.g., boolean bitmaps,
    float16, intervals, fixed-size binary), some of which are not supported
    by other constructors.
    """

    def set_data_type(self, type_id: int, element_size_bits: int = 0):
        """Set the data type used to interpret elements in :meth:`write_elements`."""
    def set_format(self, format: str):
        """Set the Python buffer format used to interpret elements in
        :meth:`write_elements`.
        """
    def format(self):
        """The ``struct`` format code of the underlying buffer"""
    def size_bytes(self):
        """The number of bytes that have been written to this buffer"""
    def capacity_bytes(self):
        """The number of bytes allocated in the underlying buffer"""
    def reserve_bytes(self, additional_bytes: int):
        """Ensure that the underlying buffer has space for ``additional_bytes``
        more bytes to be written"""
    def advance(self, additional_bytes: int):
        """Manually increase :attr:`size_bytes` by ``additional_bytes``

        This can be used after writing to the buffer using the buffer protocol
        to ensure that :attr:`size_bytes` accurately reflects the number of
        bytes written to the buffer.
        """
    def write(self, content):
        """Write bytes to this buffer

        Writes the bytes of ``content`` without considering the element type of
        ``content`` or the element type of this buffer.

        This method returns the number of bytes that were written.
        """
    def write_elements(self, obj):
        """ "Write an iterable of elements to this buffer

        Writes the elements of iterable ``obj`` according to the binary
        representation specified by :attr:`format`. This is currently
        powered by ``struct.pack_into()`` except when building bitmaps
        where an internal implementation is used.

        This method returns the number of elements that were written.
        """
    def finish(self):
        """Finish building this buffer

        Performs any steps required to finish building this buffer and
        returns the result. Any behaviour resulting from calling methods
        on this object after it has been finished is not currently
        defined (but should not crash).
        """

class NoneAwareWrapperIterator:
    """Nullable iterator wrapper

    This class wraps an iterable ``obj`` that might contain ``None`` values
    such that the iterable provided by this class contains "empty" (but valid)
    values. After ``obj`` has been completely consumed, one can call
    ``finish()`` to obtain the resulting bitmap. This is useful for passing
    iterables that might contain None to tools that cannot handle them
    (e.g., struct.pack(), array.array()).
    """

    def finish(self):
        """Obtain the total count, null count, and validity bitmap after
        consuming this iterable."""

class CArrayStream:
    """Low-level ArrowArrayStream wrapper

    This object is a literal wrapper around an ArrowArrayStream. It provides methods that
    that wrap the underlying C callbacks and handles the C Data interface lifecycle
    (i.e., initialized ArrowArrayStream structures are always released).

    See `nanoarrow.c_array_stream()` for construction and usage examples.
    """

    @staticmethod
    def _import_from_c_capsule(stream_capsule):
        """
        Import from a ArrowArrayStream PyCapsule.

        Parameters
        ----------
        stream_capsule : PyCapsule
            A valid PyCapsule with name 'arrow_array_stream' containing an
            ArrowArrayStream pointer.
        """
    def __arrow_c_stream__(self, requested_schema=None):
        """
        Export the stream as an Arrow C stream PyCapsule.

        Parameters
        ----------
        requested_schema : PyCapsule | None
            A PyCapsule containing a C ArrowSchema representation of a requested
            schema. Not supported.

        Returns
        -------
        PyCapsule
        """
    def get_schema(self):
        """Get the schema associated with this stream"""
    def get_next(self):
        """Get the next Array from this stream

        Raises StopIteration when there are no more arrays in this stream.
        """
