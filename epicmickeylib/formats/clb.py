from epicmickeylib.internal.filemanipulator import FileManipulator

import json

class CLB:

    """
    A class representing a CLB file in Epic Mickey.

    Attributes:
    - fm (FileManipulator): A FileManipulator object.
    - json_root (dict): A dictionary containing the JSON data of the CLB file.

    Methods:
    - __init__(self, data, format_type="binary", endian="big"): Initializes the CLB object.
    - decompile(self): Decompiles the binary data of the CLB object.
    - get_binary(self): Returns the binary data of the compiled CLB object.
    - get_text(self): Returns the JSON data of the CLB object as a string.
    - get_json(self): Returns the JSON data of the CLB object as a dictionary.
    """

    fm = None
    json_root = {}

    def __init__(self, data, format_type="binary", endian="big") -> None:
        """
        Initializes a CLB object.

        Args:
        - data: the data to be used to initialize the object
        - format_type: the format of the data (binary, json, or text)

        Returns:
        None
        """

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


    def decompile(self) -> None:
        """
        Decompiles the binary data and converts it to a JSON object.

        Args:
        None

        Returns:
        None
        """

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

    def get_binary(self) -> bytes:
        """
        Compiles the CLB object to binary data.

        Args:
        None

        Returns:
        bytes: the compiled binary data
        """

        self.fm = FileManipulator()
        self.fm.from_bytes(b"")

        self.fm.w_int(3)
        self.fm.w_int(len(self.json_root["collectibles"]))
        # get keys in collectibles
        for key in self.json_root["collectibles"]:
            self.fm.w_next_str(self.json_root["collectibles"][key]["type"])
            self.fm.w_next_str(key)
            self.fm.w_next_str(self.json_root["collectibles"][key]["icon"])

        self.fm.w_int(len(self.json_root["extras"]))
        # get keys in extras
        for key in self.json_root["extras"]:
            self.fm.w_next_str(self.json_root["extras"][key]["type"])
            self.fm.w_next_str(key)
            self.fm.w_next_str(self.json_root["extras"][key]["icon"])
            self.fm.w_next_str(self.json_root["extras"][key]["file"])
        return self.fm.get_bytes()

    def get_json(self) -> dict:
        """
        Returns the JSON data of the CLB object as a dictionary.

        Args:
        None

        Returns:
        dict: the JSON data of the CLB object
        """

        return self.json_root

    def get_text(self) -> str:
        """
        Returns the JSON data of the CLB object as a string.

        Args:
        None

        Returns:
        str: the JSON data of the CLB object
        """

        return json.dumps(self.json_root, indent=4)
