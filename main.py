from formats.packfile import Packfile
from utils.unpacker import Unpacker
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
packfile = None
with open(args.filename, "rb") as file:
    # get bytes
    packfile = Packfile(file.read(), "binary")

unpacker = Unpacker(packfile)
unpacker.unpack("out/", True)

#with open("test.json", "w", encoding='utf-8') as file:
#    json.dump(bsq_json, file, ensure_ascii=False, indent=4)
