from formats.scene import Scene
from formats.packfile import Packfile

path = "eb_villagetest.bin"
scene_json = {}
with open(path, "rb") as f:
    scene = Scene(f.read())
    scene_json = scene.get_json()

with open("test.bin", "wb") as f:
    scene = Scene(scene_json, "json")
    f.write(scene.get_binary())

#with open(path + ".json", "w") as f:
#    scene = Scene(scene_json, "json")
#    f.write(scene.get_text())