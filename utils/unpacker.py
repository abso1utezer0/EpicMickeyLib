from formats.packfile import Packfile
import os
import sys
from formats.scene import Scene
from formats.clb import CLB
from formats.dict import Dict


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
        paths = pak_json["order"]
        for file_path in paths:
            file = pak_json["files"][file_path]
            data = file["data"]
            extension = file_path[file_path.rfind(".") + 1:len(file_path)]
            # decompile formats
            if decompile_formats:
                if extension == "bin" or extension == "clb":# or extension == "dct":
                    # add .json to the file_path
                    file_path = file_path + ".json"

            # create directory if it doesn't exist
            dir_path = os.path.dirname(os.path.join(out_dir, file_path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            if decompile_formats:
                if extension == "bin":
                    scene = Scene(data)
                    data = scene.get_text().encode("utf-8")
                elif extension == "clb":
                    clb = CLB(data)
                    data = clb.get_text().encode("utf-8")
                #elif extension == "dct":
                #    dct = Dict(data)
                #    data = dct.get_text().encode("utf-8")

            # write file
            with open(os.path.join(out_dir, file_path), "wb") as file:
                file.write(data)
