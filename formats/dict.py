import json
from internal.filemanipulator import FileManipulator
import os
import sys

class Dict:
    fm = None
    json_root = {}
    def __init__(self, data, format_type="binary"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, "little")
            self.decompile()
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            print("Unknown type: " + type)
            sys.exit(1)
 
    def decompile(self):
        # read magic
        magic = self.fm.r_str(4) # = "DICT"

        # read version 1
        version1 = self.fm.r_int() # = 8192
        self.json_root["version1"] = version1
        print(version1)

        # read translation revision
        translation_revision = self.fm.r_int() # = ???
        self.json_root["translation_revision"] = translation_revision

        # read version 2
        version2 = self.fm.r_int() # = 19
        self.json_root["version2"] = version2

        # read line count
        line_count = self.fm.r_int() # = ???

        # move forward 4 bytes
        self.fm.move(4)

        # read footer offset - current position + r_int() + 9
        footer_offset = self.fm.tell() + self.fm.r_int() + 9

        # move forward 4 bytes
        self.fm.move(4)

        lines = {}
        footer = {}

        current_data_offset = self.fm.tell()

        # read lines
        for i in range(line_count):
            # read line id (4 bytes)
            line_id = self.fm.r_bytes(4)
            # convert to hex string (no 0x)
            line_id = line_id.hex()
            # if line id is 0, it is an empty line. add it to the lines and continue
            if line_id == "00000000":
                # get number of lines that begin with "null_"
                empty_lines = len([line for line in lines if line.startswith("null_")])
                line_id = "null_" + str(empty_lines)
                lines[line_id] = ""
                # move forward 8 bytes
                self.fm.move(8)
                continue
            # read line offset - current position + r_int() + 1
            line_offset = self.fm.tell() + self.fm.r_int() + 1
            # read line zero
            line_zero = self.fm.r_int()
            # set current data offset
            current_data_offset = self.fm.tell()
            # go to line offset
            self.fm.seek(line_offset)
            # read line - r_str_null(dct)
            line = self.fm.r_str_null()

            lines[line_id] = line
            # go to current data offset
            self.fm.seek(current_data_offset)
        # add lines to json data
        self.json_root["lines"] = lines
        while self.fm.tell() < footer_offset:
            # read footer line offset - current position + r_int(dct, 4) + 1
            footer_line_offset = self.fm.tell() + self.fm.r_int() + 1
            # read footer line id
            footer_line_id = self.fm.r_int()
            # set current data offset
            current_data_offset = self.fm.tell()
            # go to footer line offset
            self.fm.seek(footer_line_offset)
            # read footer line - r_str_null(dct)
            footer_line = self.fm.r_str_null()
            print(footer_line_offset, footer_line_id, footer_line)
            footer[footer_line] = footer_line_id
            # go to current data offset
            self.fm.seek(current_data_offset)
        # add footer to json data
        self.json_root["footer"] = footer

    def get_binary(self):
        self.fm = FileManipulator()
        self.fm.from_bytes(b"", "little")
        # get line count
        line_count = len(self.json_root["lines"])
        # get footer line count
        footer_line_count = len(self.json_root["footer"])
        end_offset = (line_count * 12) + (footer_line_count * 8) - 1
        # write magic
        self.fm.w_str("DICT")

        # write version 1
        self.fm.w_int(self.json_root["version1"])
        # write translation revision
        self.fm.w_int(self.json_root["translation_revision"])
        # write version 2
        self.fm.w_int(self.json_root["version2"])

        # write line count
        self.fm.w_int(line_count)

        # write 1
        self.fm.w_int(1)
        # write end offset
        self.fm.w_int(end_offset)
        # write 1
        self.fm.w_int(1)

        current_data_offset = self.fm.tell()
        current_line_offset = end_offset + 50
        # go to current line offset
        self.fm.seek(current_line_offset)
        # write null byte
        self.fm.w_byte(0)
        # go to current data offset
        self.fm.seek(current_data_offset)
        # write lines
        for line_id in self.json_root["lines"]:
            # get line
            line = self.json_root["lines"][line_id]
            if line_id.startswith("null_"):
                # move forward 8 bytes
                self.fm.move(8)
                continue
            # parse unicode escape sequences
            new_line = ""
            for i in range(len(line)):
                if line[i] == "\\" and line[i+1] == "u":
                    new_line += chr(int(line[i+2:i+6], 16))
                    i += 5
                else:
                    new_line += line[i]
            line = new_line
            # write line id
            line_id_bytes = b""
            for i in range(4):
                line_id_bytes += bytes.fromhex(line_id[i*2:i*2+2])
            self.fm.w_bytes(line_id_bytes)
            # write line offset
            self.fm.w_int(current_line_offset - self.fm.tell() - 1)
            # write line zero
            self.fm.w_int(0)
            current_data_offset = self.fm.tell()
            self.fm.seek(current_line_offset)
            self.fm.w_str_null(line)
            current_line_offset = self.fm.tell()
            self.fm.seek(current_data_offset)
        # write footer
        for footer_line in self.json_root["footer"]:
            # write offset
            self.fm.w_int(current_line_offset - self.fm.tell() - 1)
            # write id
            self.fm.w_int(self.json_root["footer"][footer_line])
            current_data_offset = self.fm.tell()
            # go to current line offset
            self.fm.seek(current_line_offset)
            # write line
            self.fm.w_str_null(footer_line)
            # set current line offset
            current_line_offset = self.fm.tell()
            # go to current data offset
            self.fm.seek(current_data_offset)
        # write data end bytes
        # DF FF FF FF
        self.fm.w_bytes(b"\xdf\xff\xff\xff")
        self.fm.w_int(11)
        self.fm.w_int(12)
        self.fm.w_int(0)

        return self.fm.get_bytes()

    def get_text(self):
        # convert json to text and prettify it
        return json.dumps(self.json_root, indent=4)
    
    def get_json(self):
        return self.json_root

    def __str__(self):
        return str(self.json_root)
