from utils.mass_unpacker import MassUnpacker
# import argparse
import argparse
# create application
parser = argparse.ArgumentParser(description="Unpack and decompile Epic Mickey packfiles.")
# add arguments
parser.add_argument("packfiles_dir", help="The directory to grab packfiles from.")
parser.add_argument("asset_repo", help="The asset repository to extract to.")

# parse arguments
args = parser.parse_args()

mass_unpacker = MassUnpacker(args.packfiles_dir)

mass_unpacker.mass_unpack(args.asset_repo, True)