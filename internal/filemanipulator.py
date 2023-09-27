import io
import struct

class FileManipulator:
    """
    A class for reading and manipulating binary files.

    Attributes:
    - file: The file object being manipulated.
    - endian: The endianness of the data being read.
    """

    file = None
    endian = "big"

    def __init__(self, path="", mode="rb", endian="big", encoding=None):
        """
        Initializes a new instance of the FileManipulator class.

        Args:
        - path (str): The path to the file to be manipulated.
        - mode (str): The mode in which to open the file.
        - endian (str): The endianness of the data being read.
        """
        if path != "":
            self.file = open(path, mode, encoding=encoding)
            self.endian = endian

    def from_bytes(self, data, endian="big"):
        """
        Initializes a new instance of the FileManipulator class from a bytes object.

        Args:
        - data (bytes): The bytes object to be read.
        - endian (str): The endianness of the data being read.
        """
        self.file = io.BytesIO(data)
        self.endian = endian

    def set_endian(self, endian):
        """
        Sets the endianness of the data being read.

        Args:
        - endian (str): The endianness of the data being read.
        """
        self.endian = endian

    def read_data(self, data_type, length):
        """
        Reads a specified amount of data from the file.

        Args:
        - data_type (str): The type of data to be read.
        - length (int): The length of the data to be read.

        Returns:
        - The data that was read.
        """
        self.align(4)
        value = None
        if self.endian == "big":
            value = struct.unpack(">" + data_type, self.file.read(length))[0]
        else:
            value = struct.unpack("<" + data_type, self.file.read(length))[0]
        return value

    def r_bytes(self, length):
        """
        Reads a specified amount of bytes from the file.

        Args:
        - length (int): The length of the bytes to be read.

        Returns:
        - The bytes that were read.
        """
        return self.file.read(length)
    
    def r_byte(self):
        """
        Reads a byte from the file.

        Returns:
        - The byte that was read.
        """
        return self.r_bytes(1)

    def r_int(self):
        """
        Reads a 4-byte integer from the file.

        Returns:
        - The integer that was read.
        """
        return self.read_data("i", 4)

    def r_ushort(self):
        """
        Reads a 2-byte unsigned short from the file.

        Returns:
        - The unsigned short that was read.
        """
        return self.read_data("H", 2)

    def r_float(self):
        """
        Reads a 4-byte float from the file.

        Returns:
        - The float that was read.
        """
        return self.read_data("f", 4)

    def r_bool(self):
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

    def r_str(self, length):
        """
        Reads a specified amount of characters from the file.

        Args:
        - length (int): The length of the characters to be read.

        Returns:
        - The characters that were read.
        """
        return self.file.read(length).decode("utf-8")

    def r_str_null(self):
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
        # try to decode the string byte by byte, if a character fails, try to decode it as a multiple-byte character
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
                bytes = data[i:i+1] + byte2 + byte3
                try:
                    # decode the bytes using multiple-byte character encoding
                    string += bytes.decode("utf-8")
                    i += 3
                except UnicodeDecodeError:
                    # unknown character - add its escaped unicode value
                    string += "\\u" + bytes.hex()
                    i += 3
        return string

    def move(self, amount=1):
        """
        Moves the file pointer a specified amount of bytes.

        Args:
        - amount (int): The amount of bytes to move the file pointer.
        """
        self.file.seek(self.file.tell() + amount)

    def align(self, num):
        """
        Aligns the file pointer to a specified byte boundary.

        Args:
        - num (int): The byte boundary to align the file pointer to.
        """
        pos = self.file.tell()
        if pos % num != 0:
            self.file.seek(pos + (num - (pos % num)))

    def r_next_str(self):
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
    
    def r_str_from_pointer(self, pointer):
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
    def w_data(self, data_type, data):
        """
        Writes data to the file.

        Args:
        - data_type (str): The type of data to be written.
        - data (any): The data to be written.
        """
        if self.endian == "big":
            self.file.write(struct.pack(">" + data_type, data))
        else:
            self.file.write(struct.pack("<" + data_type, data))
    
    def w_bytes(self, data):
        """
        Writes bytes to the file.

        Args:
        - data (bytes): The bytes to be written.
        """
        self.file.write(data)
    
    def w_byte(self, data):
        """
        Writes a byte to the file.

        Args:
        - data (int): The byte to be written.
        """
        self.w_bytes(bytes([data]))
    
    def w_int(self, data):
        """
        Writes a 4-byte integer to the file.

        Args:
        - data (int): The integer to be written.
        """
        self.w_data("i", data)
    
    def w_ushort(self, data):
        """
        Writes a 2-byte unsigned short to the file.

        Args:
        - data (int): The unsigned short to be written.
        """
        self.w_data("H", data)
    
    def w_float(self, data):
        """
        Writes a 4-byte float to the file.

        Args:
        - data (float): The float to be written.
        """
        self.w_data("f", data)
    
    def w_bool(self, data):
        """
        Writes a boolean value to the file.

        Args:
        - data (bool): The boolean value to be written.
        """
        if data == True:
            self.w_bytes(b"\xFF\xFF\xFF\xFF")
        else:
            self.w_bytes(b"\x00\x00\x00\x00")
    
    def w_str(self, data):
        """
        Writes a string to the file.

        Args:
        - data (str): The string to be written.
        """
        self.w_bytes(data.encode("utf-8"))
    
    def w_str_null(self, data):
        """
        Writes a null-terminated string to the file.

        Args:
        - data (str): The string to be written.
        """
        self.w_str(data)
        self.w_byte(0)
    
    def w_next_str(self, data):
        """
        Aligns the file pointer to a 4-byte boundary, then writes a null-terminated string to the file.

        Args:
        - data (str): The string to be written.
        """
        self.align(4)
        num1 = len(data) + 2
        while num1 % 4 != 0:
            num1 += 1
        num2 = len(data) + 1
        self.w_byte(num1)
        self.w_byte(num2)
        self.w_str_null(data)
        self.align(4)

    def seek(self, pos):
        """
        Sets the file pointer to a specified position.

        Args:
        - pos (int): The position to set the file pointer to.
        """
        self.file.seek(pos)

    def tell(self):
        """
        Returns the current position of the file pointer.

        Returns:
        - The current position of the file pointer.
        """
        return self.file.tell()

    def close(self):
        """
        Closes the file.
        """
        self.file.close()
    
    def get_bytes(self):
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
