import os
from formats.packfile import Packfile
from formats.scene import Scene
from formats.dict import Dict
from formats.clb import CLB
# import argparse
import argparse
# create application
parser = argparse.ArgumentParser(description="Repack an Epic Mickey packfile with updated files.")
# add arguments
parser.add_argument("asset_repo", help="The asset repository to pack from.")
parser.add_argument("packfile_path", help="The path to the packfile to parse.")

# parse arguments
args = parser.parse_args()

# check if packfile exists
if not os.path.exists(args.packfile_path):
    # throw error
    raise FileNotFoundError("Packfile not found: " + args.packfile_path)
# open packfile
packfile = None
with open(args.packfile_path, "rb") as f:
    packfile = Packfile(f.read(), format_type="binary")
packfile_json = packfile.get_json()
for file_path in packfile_json["order"]:
    # check if path is scene
    if file_path.endswith(".bin"):
        # get scene path
        decompiled = False
        scene_path = os.path.join(args.asset_repo, file_path)
        # check if scene exists
        if not os.path.exists(scene_path):
            scene_path += ".json"
        if not os.path.exists(scene_path):
            # skip
            continue
        else:
            decompiled = True
        data = None
        # open scene
        with open(scene_path, "rb") as f:
            data = f.read()
        if decompiled:
            data = data.decode("utf-8")
        scene = None
        if decompiled:
            scene = Scene(data, format_type="text")
        else:
            scene = Scene(data, format_type="binary")
        data = scene.get_binary()
        # write scene
        packfile_json["files"][file_path]["data"] = data
    #elif file_path.endswith(".dct"):
    #    # get dct path
    #    decompiled = False
    #    dct_path = os.path.join(args.asset_repo, file_path)
    #    # check if dct exists
    #    if not os.path.exists(dct_path):
    #        dct_path += ".json"
    #        if not os.path.exists(dct_path):
    #            # skip
    #            continue
    #        else:
    #            decompiled = True
    #    data = None
    #    # open dct
    #    with open(dct_path, "rb") as f:
    #        data = f.read()
    #    if decompiled == True:
    #        data = data.decode("utf-8")
    #    if decompiled == True:
    #        dct = Dict(data, format_type="text")
    #        data = dct.get_binary()
    #    
    #    # write dct
    #    packfile_json["files"][file_path]["data"] = data
    elif file_path.endswith(".clb"):
        # get clb path
        decompiled = False
        clb_path = os.path.join(args.asset_repo, file_path)
        # check if clb exists
        if not os.path.exists(clb_path):
            clb_path += ".json"
        if not os.path.exists(clb_path):
            # skip
            continue
        else:
            decompiled = True
        data = None
        # open clb
        with open(clb_path, "rb") as f:
            data = f.read()
        if decompiled:
            data = data.decode("utf-8")
        clb = None
        if decompiled:
            clb = CLB(data, format_type="text")
        else:
            clb = CLB(data, format_type="binary")
        data = clb.get_binary()
        # write clb
        packfile_json["files"][file_path]["data"] = data
    else:
        # get file path
        absolute_path = os.path.join(args.asset_repo, file_path)
        # check if file exists
        if not os.path.exists(absolute_path):
            # skip
            continue
        data = None
        # open file
        with open(absolute_path, "rb") as f:
            data = f.read()
        # write file
        packfile_json["files"][file_path]["data"] = data
# write packfile
packfile = Packfile(packfile_json, format_type="json")
data = packfile.get_binary()
with open(args.packfile_path, "wb") as f:
    f.write(data)