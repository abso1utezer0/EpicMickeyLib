import io
import struct

class FileManipulator:
    file = None
    endian = "big"

    def __init__(self, path, mode="rb", endian="big"):
        self.file = open(path, mode)
        self.endian = endian
    
    def set_endian(self, endian):
        self.endian = endian
    
    def read_data(self, type, len):
        self.align(4)
        value = None
        if self.endian == "big":
            value = struct.unpack(">" + type, self.file.read(len))[0]
        else:
            value = struct.unpack("<" + type, self.file.read(len))[0]
        self.align(4)
        return value

    def r_int(self):
        return self.read_data("i", 4)
    
    def r_ushort(self):
        return self.read_data("H", 2)
    
    def r_float(self):
        return self.read_data("f", 4)
    
    def r_bool(self):
        data = self.file.read(4)
        if data == b"\x00\x00\x00\x00":
            return False
        elif data == b"\xFF\xFF\xFF\xFF":
            return True
        else:
            raise Exception("Invalid boolean value: " + str(data))
    
    def r_str(self, len):
        return self.file.read(len).decode("utf-8")
    
    def r_str_null(self):
        string = ''.join(iter(lambda: self.file.read(1).decode('ascii'), '\x00'))
        return string
    
    def move(self, amount=1):
        self.file.seek(self.file.tell() + amount)

    def align(self, num):
        while (self.file.tell() % num) != 0:
            self.file.seek(self.file.tell() + 1)

    def r_next_str(self):
        self.align(4)
        self.move(2)
        string = self.r_str_null()
        self.align(4)
        return string