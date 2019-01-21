# cython: language_level=3

from io import RawIOBase, BytesIO, SEEK_CUR, SEEK_END, SEEK_SET, FileIO
from struct import unpack
from typing import Union, Dict

__all__ = ('ReplayReader', 'TYPE_LUA', 'ACCEPTABLE_DATA_TYPE')

TYPE_LUA = Union[int, float, str, bool, None, Dict]
ACCEPTABLE_DATA_TYPE = Union[RawIOBase, FileIO, BytesIO, bytearray, bytes]


class ReplayReader:
    """
    Handles reading data from stream and provides basic methods for parsing binary stuff.
    """

    def __init__(
            self,
            input_data: ACCEPTABLE_DATA_TYPE = b"",
            no_copy_data_source: bool=False,
            **kwargs
    ) -> None:
        self.buffer: BytesIO = None
        self.buffer_size = None  # buffer size doesn't change often, it can be cached
        self.set_data(input_data, no_copy_data_source)

    def read_string(self) -> str:
        """
        Parses string from binary data.
        """
        res = b""
        while True:
            char_ = unpack("s", self.buffer.read(1))[0]
            if char_ == b'\x00':
                break
            res += char_
        return res.decode()

    def read_number(self, type_: str = "i", size: int = 4) -> Union[int, float]:
        """
        Reads number/float/boolean by input type & size
        """
        value = unpack(type_, self.buffer.read(size))[0]
        return value

    def read_int(self) -> int:
        return self.read_number(type_="i", size=4)

    def read_short(self) -> int:
        return self.read_number(type_="H", size=2)

    def read_float(self) -> float:
        return self.read_number(type_="f", size=4)

    def read_byte(self) -> int:
        return self.read_number(type_="B", size=1)

    def read_bool(self) -> bool:
        return self.read_byte() != 0

    def read_nil(self) -> None:
        """
        Moves buffer head forward
        """
        self.buffer.read(1)
        return None

    def read_dict(self) -> Dict:
        """
        Reads more complex structure as dict
        """
        result = {}

        while self.peek_byte() != 5:
            key = self.read_lua()
            value = self.read_lua()
            result[key] = value

        self.buffer.read(1)
        return result

    def read_lua(self) -> TYPE_LUA:
        """
        Reads lua format
        """
        # determines data_type
        type_ = self.read_byte()
        if type_ == 0:
            return self.read_float()
        if type_ == 1:
            return self.read_string()
        if type_ == 2:
            return self.read_nil()
        if type_ == 3:
            return self.read_bool()
        if type_ == 4:
            return self.read_dict()

        raise ValueError("Uknown data type {} in lua format".format(type_))

    def peek_byte(self) -> int:
        """
        Peek for next byte value
        """
        value = self.read_byte()
        self.buffer.seek(-1, SEEK_CUR)
        return value

    def read(self, size=1) -> bytes:
        """
        Moves head forward
        """
        return self.buffer.read(size)

    def offset(self) -> int:
        """
        Returns internal pointer position
        """
        return self.buffer.tell()

    def size(self) -> int:
        """
        Returns size of buffer
        """
        if self.buffer_size is None:
            position = self.buffer.tell()
            self.buffer.seek(0, SEEK_END)
            end_position = self.buffer.tell()
            self.buffer.seek(position)
            self.buffer_size = end_position
        return self.buffer_size

    def seek(self, size: int, seek_type: int =SEEK_SET):
        """
        Moves offset to position in buffer
        """
        self.buffer.seek(size, seek_type)

    def set_data(self, input_data: ACCEPTABLE_DATA_TYPE, no_copy_data_source: bool = False):
        """
        Sets the current buffer for future reading.
        """
        self.buffer_size = None
        if isinstance(input_data, (RawIOBase, BytesIO, FileIO)):
            if no_copy_data_source:
                self.buffer = input_data
            else:
                # copy data and move back to previous position
                position = input_data.tell()
                input_data.seek(0)
                self.buffer = BytesIO(input_data.read())  # copy data
                input_data.seek(position)
        elif isinstance(input_data, (bytes, bytearray)):
            self.buffer_size = len(input_data)
            if not isinstance(self.buffer, BytesIO):
                self.buffer = BytesIO()
            self.buffer.truncate(self.buffer_size)
            self.buffer.seek(0)
            self.buffer.write(input_data)
            self.buffer.seek(0)
        else:
            raise ValueError("Unexpected input_data type {}. Use BytesIO, FileIO, bytes or bytearray".format(
                type(input_data)
            ))
