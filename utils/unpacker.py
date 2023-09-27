import os
from formats.dict import Dict
from formats.scene import Scene
from formats.clb import CLB

class Unpacker:
    """
    A class that unpacks a packfile to a specified output directory.

    Attributes:
    - packfile (Packfile): The packfile to be unpacked.
    """

    packfile = None

    def __init__(self, packfile):
        """
        Initializes an instance of the Unpacker class with a given packfile.

        Args:
        - packfile (Packfile): The packfile to be unpacked.
        """
        self.packfile = packfile

    def unpack(self, out_dir, decompile_formats=False):
        """
        Unpacks the packfile to a specified output directory.

        Args:
        - out_dir (str): The output directory to unpack the packfile to.
        - decompile_formats (bool): Whether or not to decompile formats.

        Returns:
        - None
        """
        pak_json = self.packfile.get_json()
        files = pak_json["files"]
        for path, file in files.items():
            data = file["data"]

            out_path = os.path.join(out_dir, path)

            # create directory if it doesn't exist
            dir_path = os.path.dirname(out_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            if decompile_formats:
                extension = path.split(".")[-1]
                magic = file["type"]
                data, new_extension = Unpacker.decompile_data(data, extension, magic)
                out_path = out_path.replace(extension, new_extension)

            # write file
            with open(out_path, "wb") as file:
                file.write(data)

    def decompile_data(data, extension, magic):
        text = ""
        extension = extension.lower()
        new_extension = extension
        magic = magic.lower()
        if extension == "dct":
            new_extension += ".json"
            dct = Dict(data)
            text = dct.get_ascii()
        elif extension == "bin":
            new_extension += ".json"
            scene = Scene(data)
            text = scene.get_text()
        elif extension == "clb":
            new_extension += ".json"
            clb = CLB(data)
            text = clb.get_text()
        else:
            return data, extension
        # encode text
        text = text.encode("utf-8")
        return text, new_extension
