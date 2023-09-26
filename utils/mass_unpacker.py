import shutil
from utils.unpacker import Unpacker
from formats.packfile import Packfile
import os
import sys

class MassUnpacker:
    asset_dir = None
    def __init__(self, asset_dir):
        self.asset_dir = asset_dir
    
    def mass_unpack(self, out_dir, decompile_formats=False):
        # get list of all files in asset_dir (recursively)
        files = []
        for root, _, filenames in os.walk(self.asset_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        # unpack all packfiles
        for file in files:
            if file.endswith(".pak"):
                with open(file, "rb") as f:
                    packfile = Packfile(f.read())
                    unpacker = Unpacker(packfile)
                    unpacker.unpack(out_dir, decompile_formats)
            else:
                if not decompile_formats:
                    # copy file to out_dir
                    out_path = file.replace(self.asset_dir, out_dir)
                    dir_path = os.path.dirname(out_path)
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                    # copy file using shutil
                    shutil.copy(file, out_path)
                else:
                    data = b""
                    extension = file.split(".")[-1]
                    with open(file, "rb") as f:
                        data = f.read()
                    data, new_extension = Unpacker.decompile_data(data, extension, "")
                    relative_path = os.path.relpath(file, self.asset_dir)
                    out_path = os.path.join(out_dir, relative_path)
                    out_path = out_path.replace(extension, new_extension)
                    dir_path = os.path.dirname(out_path)
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                    with open(out_path, "wb") as f:
                        f.write(data)