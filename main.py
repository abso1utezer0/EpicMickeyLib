from formats.bsq import BSQ
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
bsq = BSQ(args.filename)
bsq.decompile()
bsq_json = bsq.get_json()
with open("test.json", "w", encoding='utf-8') as file:
    json.dump(bsq_json, file, ensure_ascii=False, indent=4)
