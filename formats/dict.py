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

    def compile(self):
        # TODO: Implement
        pass

    def get_binary(self):
        return self.compile()

    def get_text(self):
        # convert json to text and prettify it
        return json.dumps(self.json_root, indent=4)
    
    def get_json(self):
        return self.json_root

    def __str__(self):
        return str(self.json_root)
