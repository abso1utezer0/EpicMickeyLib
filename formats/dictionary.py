import json
from internal.filemanipulator import FileManipulator
import os
import sys

class Dictionary:
    """
    A class representing a dictionary file in Epic Mickey.

    Attributes:
    - fm (FileManipulator): A FileManipulator object.
    - json_root (dict): A dictionary containing the JSON data of the dictionary file.

    Methods:
    - __init__(self, data, format_type="binary"): Initializes the Dictionary object.
    - decompile(self): Decompiles the binary data of the Dictionary object.
    - get_binary(self): Returns the binary data of the compiled Dictionary object.
    - get_text(self): Returns the JSON data of the Dictionary object as a string.
    - get_json(self): Returns the JSON data of the Dictionary object as a dictionary.
    """

    fm = None
    json_root = {}

    def __init__(self, data, format_type="binary") -> None:

        """
        Initializes a Dictionary object.

        Args:
        - data: the data to be used to initialize the object
        - format_type: the format of the data (binary, json, or text)

        Returns:
        None
        """

        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, "little")
            self.decompile()
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            raise ValueError(f"Invalid format type specified: {format_type}. Must be 'binary', 'json', or 'text'.")
 
    def decompile(self) -> None:

        """
        Decompiles the binary data and converts it to a JSON object.

        Args:
        None

        Returns:
        None
        """

        # read magic
        magic = self.fm.r_str(4) # = "DICT"

        # read version 1
        version1 = self.fm.r_int() # = 8192

        # read translation revision
        revision = self.fm.r_bytes(4)
        revision = revision.hex()
        self.json_root["revision"] = revision

        # read version 2
        version2 = self.fm.r_int() # = 19

        # read line count
        line_count = self.fm.r_int() # = ???

        # move forward 4 bytes
        self.fm.move(4)

        # read footer offset - current position + r_int() + 9
        footer_offset = self.fm.tell() + self.fm.r_int() + 9

        # move forward 4 bytes
        self.fm.move(4)

        lines = []
        footer = []

        current_data_offset = self.fm.tell()

        # read lines
        for i in range(line_count):
            line = {}
            # read line id (4 bytes)
            line_id = self.fm.r_bytes(4)
            # convert to hex string (no 0x)
            line_id = line_id.hex()
            # if line id is 0, it is an empty line. add it to the lines and continue
            if line_id == "00000000":
                # move forward 8 bytes
                self.fm.move(8)
                lines.append(line)
                current_data_offset = self.fm.tell()
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
            line_text = self.fm.r_str_null()

            line["id"] = line_id
            line["text"] = line_text

            lines.append(line)

            # go to current data offset
            self.fm.seek(current_data_offset)
        # add lines to json data
        self.json_root["lines"] = lines
        while self.fm.tell() < footer_offset:
            footer_line = {}
            # read footer line offset - current position + r_int(dct, 4) + 1
            footer_line_offset = self.fm.tell() + self.fm.r_int() + 1
            # read footer line id
            footer_line_id = self.fm.r_int()
            # set current data offset
            current_data_offset = self.fm.tell()
            # go to footer line offset
            self.fm.seek(footer_line_offset)
            # read footer line - r_str_null(dct)
            footer_line_text = self.fm.r_str_null()
            # add footer line to footer
            footer_line["id"] = footer_line_id
            footer_line["text"] = footer_line_text
            footer.append(footer_line)
            # go to current data offset
            self.fm.seek(current_data_offset)
        # add footer to json data
        self.json_root["footer"] = footer

    def get_binary(self) -> bytes:

        """
        Returns the binary data for the Dictionary object.

        Args:
        None

        Returns:
        The binary data for the Dictionary object.
        """

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
        self.fm.w_int(8192)
        # get revision
        revision = self.json_root["revision"]
        # convert revision to bytes
        revision_bytes = bytes.fromhex(revision)
        # write revision
        self.fm.w_bytes(revision_bytes)
        # write version 2
        self.fm.w_int(19)

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
        for line in self.json_root["lines"]:
            # if line has no id, it is an empty line. write 0 and continue
            if not "id" in line:
                for i in range(3):
                    self.fm.w_int(0)
                current_data_offset = self.fm.tell()
                continue
            line_id = line["id"]
            line_text = line["text"]
            # parse unicode escape sequences
            new_line_text = ""
            for i in range(len(line_text)):
                if line_text[i] == "\\":
                    if line_text[i+1] == "u":
                        new_line_text += chr(int(line_text[i+2:i+6], 16))
                        i += 5
                    else:
                        new_line_text += line_text[i]
                else:
                    new_line_text += line_text[i]
            line_text = new_line_text
            # write line id
            line_id = bytes.fromhex(line_id)
            self.fm.w_bytes(line_id)
            # write line offset
            self.fm.w_int(current_line_offset - self.fm.tell() - 1)
            # write line zero
            self.fm.w_int(0)
            current_data_offset = self.fm.tell()
            self.fm.seek(current_line_offset)
            self.fm.w_str_null(line_text)
            current_line_offset = self.fm.tell()
            self.fm.seek(current_data_offset)
        # write footer
        for footer_line in self.json_root["footer"]:
            footer_line_id = footer_line["id"]
            footer_line_text = footer_line["text"]
            # write offset
            self.fm.w_int(current_line_offset - self.fm.tell() - 1)
            # write id
            self.fm.w_int(footer_line_id)
            current_data_offset = self.fm.tell()
            # go to current line offset
            self.fm.seek(current_line_offset)
            # write line
            self.fm.w_str_null(footer_line_text)
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

    def get_text(self) -> str:

        """
        Returns the JSON representation of the dictionary object as a formatted string.

        Args:
        None

        Returns:
        The JSON representation of the dictionary object as a formatted string.
        """

        # convert json to text and prettify it
        return json.dumps(self.json_root, indent=4)
    
    def get_json(self) -> dict:

        """
        Returns the JSON representation of the dictionary object as a dictionary.

        Args:
        None

        Returns:
        The JSON representation of the dictionary object as a dictionary.
        """

        return self.json_root

    def __str__(self) -> str:

        """
        Returns the JSON representation of the dictionary object as a formatted string.
    
        Args:
        None

        Returns:
        The JSON representation of the dictionary object as a formatted string.
        """
        
        return self.get_text()
