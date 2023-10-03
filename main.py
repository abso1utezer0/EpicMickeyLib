import io
from formats.packfile import Packfile
import os
import sys
import argparse
from generated.formats.nif import NifFile
from generated.formats.nif.enums.EndianType import EndianType

# create application
parser = argparse.ArgumentParser(description="Repack an Epic Mickey packfile with updated files.")

# add arguments
parser.add_argument("packfile_path", help="The path to the packfile to parse.")
parser.add_argument("file_to_replace_with", help="The file to replace with.")

# parse arguments
args = parser.parse_args()

packfile_path = args.packfile_path

packfile = None
with open(packfile_path, "rb") as f:
    packfile = Packfile(f.read(), format_type="binary")
packfile_json = packfile.get_json()

#print(packfile_json)

file_to_replace = "environments/nos/props/NOS_alligator_01a_inert.nif"

# open file to replace with
nif = NifFile().from_path(args.file_to_replace_with)
nif.endian_type = EndianType.ENDIAN_LITTLE
nif.user_version = 17
for block in nif.blocks:
    # if block is a texture
    if block.__class__.__name__ == "NiSourceTexture":
        # if there is a file path
        if block.file_name != "" and block.file_name != None:
            # replace file path
            block.file_path = "\\environments\\nos\\props\\gen3\\G3_NOS_alligator_01a_inert_D_tex.nif"
            #print(block.file_path)
print(nif)
# create empty stream
data = io.BytesIO()
# write nif to stream
NifFile.to_stream(nif, data)

# convert stream to bytes
data = data.getvalue()

# save file to temp file
with open("temp.nif", "wb") as f:
    f.write(data)

# replace file
packfile_json["files"][file_to_replace]["data"] = data

packfile = Packfile(packfile_json, format_type="json")
with open(packfile_path, "wb") as f:
    f.write(packfile.get_binary(endian="little"))
