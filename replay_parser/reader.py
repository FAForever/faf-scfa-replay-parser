from io import RawIOBase, BytesIO, SEEK_CUR, SEEK_END
from struct import unpack
from typing import Union, Dict

from .config import debug

__all__ = ('ReplayReader', 'TYPE_LUA')

TYPE_LUA = Union[int, float, str, bool, None, Dict]


class ReplayReader:
    """
    Class that handles reading data from stream.
    """

    def __init__(self, input_data: Union[RawIOBase, BytesIO, bytearray, bytes]):
        self.data: BytesIO = None
        if isinstance(input_data, (RawIOBase, BytesIO)):
            # copy data and move back to previous position
            position = input_data.tell()
            input_data.seek(0)
            self.data = BytesIO(input_data.read())  # copy data
            input_data.seek(position)
        elif isinstance(input_data, (bytes, bytearray)):
            self.data = BytesIO(input_data)  # copy data

    @debug
    def read_string(self) -> str:
        """
        Parses string from binary data.
        """
        res = b""
        while True:
            char_ = unpack("s", self.data.read(1))[0]
            if char_ == b'\x00':
                break
            res += char_
        return res.decode()

    def read_number(self, type_: str = "i", size: int = 4) -> Union[int, float]:
        """
        Reads number/float/boolean by input type & size
        """
        value = unpack(type_, self.data.read(size))[0]
        return value

    @debug
    def read_int(self) -> int:
        return self.read_number(type_="i", size=4)

    @debug
    def read_float(self) -> float:
        return self.read_number(type_="f", size=4)

    @debug
    def read_byte(self) -> int:
        return self.read_number(type_="B", size=1)

    @debug
    def read_bool(self) -> bool:
        return self.read_byte() != 0

    @debug
    def read_nil(self) -> None:
        """
        Moves head forward
        """
        self.data.read(1)
        return None

    @debug
    def read_dict(self) -> Dict:
        """
        Reads more complex structure as dict
        """
        result = {}

        while self.peek_byte() != 5:
            key = self.read_lua()
            value = self.read_lua()
            result[key] = value

        self.data.read(1)
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

    @debug
    def peek_byte(self) -> int:
        """
        Peek for next byte value
        """
        value = self.read_byte()
        self.data.seek(-1, SEEK_CUR)
        return value

    @debug
    def read(self, size=1):
        """
        Moves head forward
        """
        return self.data.read(size)

    @debug
    def offset(self):
        """
        Returns internal pointer position
        """
        return self.data.tell()

    @debug
    def size(self):
        position = self.data.tell()
        self.data.seek(0, SEEK_END)
        end_position = self.data.tell()
        self.data.seek(position)
        return end_position
