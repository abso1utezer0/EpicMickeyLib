from utils.packer import Packer
# import argparse
import argparse
# create application
parser = argparse.ArgumentParser(description="Pack an Epic Mickey scene into a packfile.")
# add arguments
parser.add_argument("asset_repo", help="The asset repository to pack from.")
parser.add_argument("scene_path", help="The path to the scene to pack (relative to the asset repository).")
parser.add_argument("packfiles_dir", help="The directory to output the packfiles to.")

# parse arguments
args = parser.parse_args()

packer = Packer(args.asset_repo)

packer.pack_from_scene(args.scene_path.replace(".json", ""), args.packfiles_dir)