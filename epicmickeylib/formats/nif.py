import sys
from generated.formats.nif import NifFile
import json
from epicmickeylib.internal.filemanipulator import FileManipulator
import io

class Nif:
    json_root = {}
    nif = None
    def __init__(self, data, format_type="binary"):
        if format_type == "binary":
            # create empty stream
            stream = io.BytesIO()
            # write data to stream
            stream.write(data)
            self.nif = NifFile().from_stream(stream)
            
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            print("Unknown type: " + type)
            sys.exit(1)
    
    