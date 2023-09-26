from internal.filemanipulator import FileManipulator
import os
import sys
import json

class CLB:
    fm = None
    json_root = {}

    def __init__(self, data, format_type="binary", endian="big"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, endian)
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            raise Exception("Invalid format type specified.")
    
    def decompile(self):
        
        collectibles = {}

        # move 4 bytes forward
        self.fm.move(4)
        collectibles_amount = self.fm.r_int()
        for i in range(collectibles_amount):
            collectible = {}
            object_type = self.fm.r_next_str()
            collectible["type"] = object_type
            name = self.fm.r_next_str()
            icon_path = self.fm.r_next_str()
            collectible["icon"] = icon_path

            collectibles[name] = collectible
        
        extras = {}
        extras_amount = self.fm.r_int()
        for i in range(extras_amount):
            extra = {}
            object_type = self.fm.r_next_str()
            extra["type"] = object_type
            name = self.fm.r_next_str()
            icon_path = self.fm.r_next_str()
            extra["icon"] = icon_path
            file_path = self.fm.r_next_str()
            extra["file"] = file_path

            extras[name] = extra
        
        self.json_root["collectibles"] = collectibles
        self.json_root["extras"] = extras
            
    def get_json(self):
        return self.json_root
    
    def get_binary(self):
        # TODO: implement
        return b""
    
    def get_text(self):
        return json.dumps(self.json_root, indent=4)

