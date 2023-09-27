from formats.scene import Scene
from formats.packfile import Packfile

path = "E:/Modding/EpicMickey/Builds/EM1/clean/DATA/files/packfiles/_Dynamic.pak"
pack_json = {}
with open(path, "rb") as f:
    packfile = Packfile(f.read())
    pack_json = packfile.get_json()
scene = None
for path in pack_json["order"]:
    if path.endswith(".bin"):
        scene = Scene(pack_json["files"][path]["data"])
        break

print(scene.get_referenced_files())