import shutil
from utils.unpacker import Unpacker
from formats.packfile import Packfile
import os
import sys

class MassUnpacker:
    packfile_dir = None
    def __init__(self, packfile_dir):
        self.packfile_dir = packfile_dir
    
    def mass_unpack(self, out_dir, decompile_formats=False):
        # loop through packfiles
        for file in os.listdir(self.packfile_dir):
            if file.endswith(".pak"):
                file = os.path.join(self.packfile_dir, file)
                with open(file, "rb") as f:
                    packfile = Packfile(f.read())
                    unpacker = Unpacker(packfile)
                    unpacker.unpack(out_dir, decompile_formats)
        # check if palettes/_dynamic.bin.json exists
        dynamic_exists = False
        while dynamic_exists == False:
            if os.path.exists(os.path.join(out_dir, "Palettes", "_Dynamic.bin.json")):
                dynamic_exists = True
            else:
                # decompile _dynamic.pak
                dynamic_pak = os.path.join(self.packfile_dir, "_Dynamic.pak")
                with open(dynamic_pak, "rb") as f:
                    packfile = Packfile(f.read())
                    unpacker = Unpacker(packfile)
                    unpacker.unpack(out_dir, decompile_formats)