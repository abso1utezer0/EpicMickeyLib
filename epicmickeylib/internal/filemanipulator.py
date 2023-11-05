"""
A module for reading and manipulating binary files.
"""
import io
import struct

class FileManipulator:

    """
    A class for reading and manipulating binary files.

    Attributes:
    - file: The file object being manipulated.
    - endian: The endianness of the data being read.
    - write_mode: The write mode of the file. Can be "overwrite" or "insert".
    """

    file = None
    endian = "big"
    write_mode = "overwrite"

    def __init__(self, path="", mode="rb", endian="big", encoding=None) -> None:

        """
        Initializes a new instance of the FileManipulator class.

        Args:
        - path (str): The path to the file to be manipulated.
        - mode (str): The mode in which to open the file.
        - endian (str): The endianness of the data being read.
        - encoding (str): The encoding of the file to be manipulated.

        Returns:
        None
        """

        if path != "":
            self.file = open(path, mode, encoding=encoding)
            self.endian = endian

    def from_bytes(self, data, endian="big") -> None:

        """
        Initializes a new instance of the FileManipulator class from a bytes object.

        Args:
        - data (bytes): The bytes object to be read.
        - endian (str): The endianness of the data being read.
        
        Returns:
        None
        """

        self.file = io.BytesIO(data)
        self.endian = endian

    def set_endian(self, endian) -> None:
        """
        Sets the endianness of the data being read.

        Args:
        - endian (str): The endianness of the data being read.
        
        Returns:
        None
        """
        self.endian = endian.lower()

    def read_data(self, data_type, length) -> any:

        """
        Reads a specified amount of data from the file.

        Args:
        - data_type (str): The type of data to be read.
        - length (int): The length of the data to be read.

        Returns:
        - The data that was read.
        """

        #self.align(4)
        value = None
        if self.endian == "big":
            value = struct.unpack(">" + data_type, self.file.read(length))[0]
        else:
            value = struct.unpack("<" + data_type, self.file.read(length))[0]
        return value

    def r_bytes(self, length) -> bytes:
        """
        Reads a specified amount of bytes from the file.

        Args:
        - length (int): The length of the bytes to be read.

        Returns:
        - The bytes that were read.
        """
        return self.file.read(length)

    def r_byte(self) -> int:
        """
        Reads a byte from the file.

        Returns:
        - The byte that was read.
        """
        return self.r_bytes(1)
    
    def r_uint(self) -> int:
            
        """
        Reads a 4-byte unsigned integer from the file.

        Returns:
        - The unsigned integer that was read.
        """

        return self.read_data("I", 4)
    
    def r_int(self) -> int:
                
        """
        Reads a 4-byte integer from the file.

        Returns:
        - The integer that was read.
        """

        return self.read_data("i", 4)

    def r_ushort(self) -> int:

        """
        Reads a 2-byte unsigned short from the file.

        Returns:
        - The unsigned short that was read.
        """

        return self.read_data("H", 2)
    
    def r_short(self) -> int:
            
            """
            Reads a 2-byte short from the file.
    
            Returns:
            - The short that was read.
            """
    
            return self.read_data("h", 2)

    def r_float(self) -> float:

        """
        Reads a 4-byte float from the file.

        Returns:
        - The float that was read.
        """

        return self.read_data("f", 4)

    def r_bool(self) -> bool:

        """
        Reads a boolean value from the file.

        Returns:
        - The boolean value that was read.
        """

        data = self.file.read(4)
        if data == b"\x00\x00\x00\x00":
            return False
        elif data == b"\xFF\xFF\xFF\xFF":
            return True
        else:
            raise ValueError("Invalid boolean value: " + str(data))

    def r_str(self, length) -> str:

        """
        Reads a specified amount of characters from the file.

        Args:
        - length (int): The length of the characters to be read.

        Returns:
        - The characters that were read.
        """

        return self.file.read(length).decode("utf-8")

    def r_str_null(self) -> str:

        """
        Reads a null-terminated string from the file.

        Returns:
        - The string that was read.
        """

        data = b""
        while True:
            byte = self.file.read(1)
            if byte == b"\x00":
                break
            else:
                data += byte
        string = ""
        # try to decode the string byte by byte,
        # if a character fails,
        # try to decode it as a multiple-byte character
        i = 0
        while i < len(data):
            try:
                string += data[i:i+1].decode("utf-8")
                i += 1
            except UnicodeDecodeError:
                # multiple-byte character
                # get the next 2 bytes
                byte2 = data[i+1:i+2]
                byte3 = data[i+2:i+3]
                # combine the bytes
                code_bytes = data[i:i+1] + byte2 + byte3
                try:
                    # decode the bytes using multiple-byte character encoding
                    string += code_bytes.decode("utf-8")
                    i += 3
                except UnicodeDecodeError:
                    # unknown character - add its escaped unicode value
                    string += "\\u" + code_bytes.hex()
                    i += 3
        return string

    def move(self, amount=1) -> None:

        """
        Moves the file pointer a specified amount of bytes.

        Args:
        - amount (int): The amount of bytes to move the file pointer.
        """

        self.file.seek(self.file.tell() + amount)

    def align(self, num) -> None:

        """
        Aligns the file pointer to a specified byte boundary.

        Args:
        - num (int): The byte boundary to align the file pointer to.
        """

        pos = self.file.tell()
        if pos % num != 0:
            self.file.seek(pos + (num - (pos % num)))

    def r_next_str(self) -> str:

        """
        Reads the next null-terminated string from the file.

        Returns:
        - The string that was read.
        """

        self.align(4)
        self.move(2)
        string = self.r_str_null()
        self.align(4)
        return string

    def r_str_from_pointer(self, pointer) -> str:

        """
        Reads a null-terminated string from a specified pointer.

        Args:
        - pointer (int): The pointer to read the string from.

        Returns:
        - The string that was read.
        """

        pos = self.file.tell()
        self.file.seek(pointer + 2)
        string = self.r_str_null()
        self.file.seek(pos)
        return string

    def w_data(self, data_type, data) -> None:

        """
        Writes data to the file.

        Args:
        - data_type (str): The type of data to be written.
        - data (any): The data to be written.
        """

        data_to_write = None
        if self.endian == "big":
            data_to_write = struct.pack(">" + data_type, data)
        else:
            data_to_write = struct.pack("<" + data_type, data)

        if self.write_mode == "overwrite":
            self.file.write(data_to_write)
        elif self.write_mode == "insert":
            # insert data
            pos = self.file.tell()
            data = self.file.read()
            self.file.seek(pos)
            self.file.write(data_to_write)
            self.file.write(data)
            # move file pointer
            self.file.seek(pos + len(data_to_write))
        else:
            raise ValueError(f"""
                Invalid write mode specified: {self.write_mode}. Must be 'overwrite' or 'insert'.
            """)

    def w_bytes(self, data) -> None:

        """
        Writes bytes to the file.

        Args:
        - data (bytes): The bytes to be written.
        """

        self.file.write(data)

    def w_byte(self, data) -> None:

        """
        Writes a byte to the file.

        Args:
        - data (int): The byte to be written.
        """

        self.w_bytes(bytes([data]))
    
    def w_uint(self, data) -> None:
            
        """
        Writes a 4-byte unsigned integer to the file.

        Args:
        - data (int): The unsigned integer to be written.
        """

        self.w_data("I", data)

    def w_int(self, data) -> None:

        """
        Writes a 4-byte integer to the file.

        Args:
        - data (int): The integer to be written.
        """

        self.w_data("i", data)

    def w_ushort(self, data) -> None:

        """
        Writes a 2-byte unsigned short to the file.

        Args:
        - data (int): The unsigned short to be written.
        """

        self.w_data("H", data)
    
    def w_short(self, data) -> None:
            
        """
        Writes a 2-byte short to the file.

        Args:
        - data (int): The short to be written.
        """

        self.w_data("h", data)


    def w_float(self, data) -> None:

        """
        Writes a 4-byte float to the file.

        Args:
        - data (float): The float to be written.
        """

        self.w_data("f", data)

    def w_bool(self, data) -> None:

        """
        Writes a boolean value to the file.

        Args:
        - data (bool): The boolean value to be written.
        """

        if data is True:
            self.w_bytes(b"\xFF\xFF\xFF\xFF")
        else:
            self.w_bytes(b"\x00\x00\x00\x00")

    def w_str(self, data) -> None:

        """
        Writes a string to the file.

        Args:
        - data (str): The string to be written.
        """

        self.w_bytes(data.encode("utf-8"))

    def w_str_null(self, data) -> None:

        """
        Writes a null-terminated string to the file.

        Args:
        - data (str): The string to be written.
        """

        self.w_str(data)
        self.w_byte(0)

    def w_next_str(self, data) -> None:

        """
        Aligns the file pointer to a 4-byte boundary,
        then writes a null-terminated string to the file.

        Args:
        - data (str): The string to be written.
        """

        self.align(4)
        num1 = 2
        num1 += len(data) + 1
        while num1 % 4 != 0:
            num1 += 1
        num2 = len(data) + 1
        if len(data) == 0:
            num2 = 0
        self.w_byte(num1)
        self.w_byte(num2)
        self.w_str_null(data)
        self.align(4)

    def seek(self, pos) -> None:

        """
        Sets the file pointer to a specified position.

        Args:
        - pos (int): The position to set the file pointer to.
        """

        self.file.seek(pos)

    def tell(self) -> int:

        """
        Returns the current position of the file pointer.

        Args:
        None

        Returns:
        - The current position of the file pointer.
        """

        return self.file.tell()

    def close(self) -> None:

        """
        Closes the file.
        """

        self.file.close()

    def get_bytes(self) -> bytes:

        """
        Returns the bytes of the file.

        Returns:
        - The bytes of the file.
        """

        # get current position
        pos = self.file.tell()
        # seek to beginning
        self.file.seek(0)
        # read bytes
        data = self.file.read()
        # seek to original position
        self.file.seek(pos)
        # return bytes
        return data

    def size(self) -> int:

        """
        Returns the size of the file.

        Returns:
        - The size of the file.
        """

        # get current position
        pos = self.file.tell()
        # seek to end
        self.file.seek(0, 2)
        # get size
        size = self.file.tell()
        # seek to original position
        self.file.seek(pos)
        # return size
        return size

    def set_write_mode(self, mode) -> None:

        """
        Sets the write mode of the file.

        Args:
        - mode (str): The write mode to set.
        """

        self.write_mode = mode
