class CBufferBuilder :
    """Wrapper around writable CPU buffer content

    This class provides a growable type-aware buffer that can be used
    to create a typed buffer from a Python iterable. This method of
    creating a buffer is usually slower than constructors like
    ``array.array()`` or ``numpy.array()``; however, this class supports
    all Arrow types with a single data buffer (e.g., boolean bitmaps,
    float16, intervals, fixed-size binary), some of which are not supported
    by other constructors.
    """

    def set_data_type (self ,type_id :ArrowType ,element_size_bits :int =0 ):
        """Set the data type used to interpret elements in :meth:`write_elements`."""

    def set_format (self ,format :str ):
        """Set the Python buffer format used to interpret elements in
        :meth:`write_elements`.
        """

    def format (self ):
        """The ``struct`` format code of the underlying buffer"""

    def size_bytes (self ):
        """The number of bytes that have been written to this buffer"""

    def capacity_bytes (self ):
        """The number of bytes allocated in the underlying buffer"""

    def reserve_bytes (self ,additional_bytes :int64_t ):
        """Ensure that the underlying buffer has space for ``additional_bytes``
        more bytes to be written"""

    def advance (self ,additional_bytes :int64_t ):
        """Manually increase :attr:`size_bytes` by ``additional_bytes``

        This can be used after writing to the buffer using the buffer protocol
        to ensure that :attr:`size_bytes` accurately reflects the number of
        bytes written to the buffer.
        """

    def write (self ,content ):
        """Write bytes to this buffer

        Writes the bytes of ``content`` without considering the element type of
        ``content`` or the element type of this buffer.

        This method returns the number of bytes that were written.
        """

    def write_elements (self ,obj ):
        """"Write an iterable of elements to this buffer

        Writes the elements of iterable ``obj`` according to the binary
        representation specified by :attr:`format`. This is currently
        powered by ``struct.pack_into()`` except when building bitmaps
        where an internal implementation is used.

        This method returns the number of elements that were written.
        """

    def finish (self ):
        """Finish building this buffer

        Performs any steps required to finish building this buffer and
        returns the result. Any behaviour resulting from calling methods
        on this object after it has been finished is not currently
        defined (but should not crash).
        """

