from formats.packfile import Packfile
import os
import sys


class Unpacker:
    packfile = None

    def __init__(self, packfile):
        """
        Initializes an instance of the Unpacker class with a given packfile.

        Args:
        packfile (Packfile): The packfile to be unpacked.
        """
        self.packfile = packfile

    def unpack(self, out_dir, decompile_formats=False):
        """
        Unpacks the packfile to a specified output directory.

        Args:
        - out_dir (str): The output directory to unpack the packfile to.
        - decompile_formats (bool): Whether or not to decompile formats.

        Returns:
        None
        """
        pak_json = self.packfile.get_json()
        files = pak_json["files"]
        keys = list(files.keys())
        for i in range(len(keys)):
            path = keys[i]
            file = files[path]
            data = file["data"]

            # create directory if it doesn't exist
            dir_path = os.path.dirname(out_dir + path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # write file
            with open(out_dir + path, "wb") as file:
                file.write(data)
