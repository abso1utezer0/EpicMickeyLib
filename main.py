from utils.mass_unpacker import MassUnpacker

if __name__ == "__main__":
    input_dir = "E:/Modding/EpicMickey/BuildsEx/EM1/"
    output_dir = "E:/JunctionPoint/Mickey/Game/Content/Raw/"
    unpacker = MassUnpacker(input_dir)
    unpacker.mass_unpack(output_dir, True)