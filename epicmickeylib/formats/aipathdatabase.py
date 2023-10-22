from epicmickeylib.internal.filemanipulator import FileManipulator
import json

class AIPathDatabase:
    fm = None
    json_root = {}

    def __init__(self, data, format_type="binary", endian="little"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, endian)
            self.decompile()
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            raise ValueError(f"Invalid format type specified: {format_type}. Must be 'binary', 'json', or 'text'.")
    
    def decompile(self):
        self.fm.seek(0x10)
        num_vertices = self.fm.r_int()
        num_faces = self.fm.r_int()
        section1 = []
        section2 = []
        for i in range(num_vertices):
            unknown_int1 = self.fm.r_int()
            x = self.fm.r_float()
            y = self.fm.r_float()
            z = self.fm.r_float()
            unknown1 = self.fm.r_bytes(4)
            unknown2 = self.fm.r_bytes(4)
            # convert unknown 1 to hex string, no 0x
            unknown1 = unknown1.hex()
            # convert unknown 2 to hex string, no 0x
            unknown2 = unknown2.hex()
            unknown_int2 = self.fm.r_int()
            unknown_float3 = self.fm.r_float()
            unknown_int3 = self.fm.r_int()
            

            entry = {}
            entry["position"] = [x, y, z]
            entry["unknown1"] = unknown1
            entry["unknown2"] = unknown2
            entry["unknown_int1"] = unknown_int1
            entry["unknown_float3"] = unknown_float3
            entry["unknown_int2"] = unknown_int2
            entry["unknown_int3"] = unknown_int3
            section1.append(entry)
        self.fm.move(-4)
        for i in range(num_faces):
            target = self.fm.r_int()
            unknown1 = self.fm.r_bytes(4)
            # convert unknown 1 to hex string, no 0x
            unknown1 = unknown1.hex()
            unknown2 = self.fm.r_int()

            entry = {}
            entry["target"] = target
            entry["unknown1"] = unknown1
            entry["unknown2"] = unknown2
            section2.append(entry)
        sections = []
        sections.append(section1)
        sections.append(section2)
        self.json_root["sections"] = sections

    def get_json(self):
        return self.json_root
    
    def get_text(self):
        return json.dumps(self.json_root, indent=4)