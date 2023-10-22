import os
import zlib
from epicmickeylib.formats.dictionary import Dictionary
from epicmickeylib.formats.packfile import Packfile
from epicmickeylib.formats.scene import Scene
from epicmickeylib.formats.clb import CLB
from generated.formats.nif import NifFile

class Packer:
    """
    A class that packs a packfile to a specified output directory.

    Attributes:
    - packfile (Packfile): The packfile to be unpacked.
    """

    base_dir = None
    paths_to_exclude = []

    def __init__(self, base_dir):
        self.base_dir = base_dir.replace("\\", "/")

    def check_if_filetype_is_compressed(self, filetype):
        return False
        filetype = filetype.lower()
        if filetype == "":
            return True
        elif filetype == "lua":
            return True
        elif filetype == "nif":
            return False
        elif filetype == "kf":
            return False
        elif filetype == "kfm":
            return False
        else:
            return False
    
    def find_palette(self, palette_name):
        palette_path = ""
        for root, _, filenames in os.walk(os.path.join(self.base_dir, "palettes")):
            for filename in filenames:
                # if the filename is the palette name + .bin or .bin.json
                if filename.lower() == palette_name.lower() + ".bin" or filename.lower() == palette_name.lower() + ".bin.json":
                    # return the relative path to the palette
                    palette_path = os.path.join(root, filename).replace(".json", "")
                    palette_path = os.path.relpath(palette_path, self.base_dir)
                    palette_path = palette_path.replace("\\", "/")
                    break
        return palette_path
    
    def get_referenced_files_for_nif(self, relative_path):
        paths = []
        filetypes = []
        nif = NifFile.from_path(os.path.join(self.base_dir, relative_path))
        for block in nif.blocks:
            # if the class name is NiSourceTexture
            if block.__class__.__name__ == "NiSourceTexture":
                # get the file name
                file_name = block.file_name
                if file_name:
                    file_name = file_name.replace("\\", "/")
                    # remove the first slash if it exists
                    if file_name[0] == "/":
                        file_name = file_name[1:len(file_name)]
                    # check if file exists, if not, add _wii to the end
                    if not os.path.exists(os.path.join(self.base_dir, file_name)):
                        file_name += "_wii"
                    # check if file exists, if not, skip it
                    if not os.path.exists(os.path.join(self.base_dir, file_name)):
                        continue
                    # add the file to the paths
                    paths.append(file_name)
                    filetypes.append("nif")
        return paths, filetypes
    
    def get_referenced_files_for_file(self, relative_path):
        paths = []
        filetypes = []
        if relative_path.endswith(".nif") or relative_path.endswith(".nif_wii"):
            paths, filetypes = self.get_referenced_files_for_nif(relative_path)
            # prepend the relative path to the paths
            paths = [relative_path] + paths
            filetypes = ["nif"] + filetypes
        return paths, filetypes

    
    def get_referenced_files_for_scene(self, relative_path):
        paths = []
        filetypes = []
        palettes = []
        scene = Scene(self.get_file_bytes(relative_path), "binary")
        palettes = scene.get_referenced_palettes()
        if len(palettes) == 0:
            # exit if there are no palettes
            return paths, filetypes
        for palette in palettes:
            palette_path = self.find_palette(palette)
            if palette_path != "" and palette_path is not None and palette_path not in paths:
                exclude = False
                for path in self.paths_to_exclude:
                    if path.lower() == palette_path.lower():
                        exclude = True
                if not exclude:
                    print("Adding palette: " + palette_path)
                    paths.append(palette_path)
                    filetypes.append("")
                    ## get the referenced files for the palette
                    #sub_paths, sub_filetypes = self.get_referenced_files_for_scene(palette_path)
                    ## add the sub paths and sub filetypes to the paths and filetypes
                    #paths += sub_paths
                    #filetypes += sub_filetypes
        other_paths, other_filetypes = scene.get_referenced_files()
        for i in range(len(other_paths)):
            path = other_paths[i]
            # if path doesnt exist, add _wii to the end
            if not os.path.exists(os.path.join(self.base_dir, path)):
                path += "_wii"
            if not os.path.exists(os.path.join(self.base_dir, path)):
                # if path still doesnt exist, skip it
                continue
            filetype = other_filetypes[i]
            exclude = False
            for path_to_exclude in self.paths_to_exclude:
                if path_to_exclude.lower() == path.lower():
                    exclude = True
            if not exclude:
                new_paths, new_filetypes = self.get_referenced_files_for_file(path)
                paths += new_paths
                filetypes += new_filetypes
                paths.append(path)
                filetypes.append(filetype)
        return paths, filetypes
    
    def get_file_bytes(self, relative_path):
        data = b""
        extension = relative_path.split(".")[-1]
        decompiled = False
        # check if relative_path + .json exists
        if os.path.exists(os.path.join(self.base_dir, relative_path + ".json")):
            decompiled = True
            relative_path += ".json"
        with open(os.path.join(self.base_dir, relative_path), "rb") as f:
            # read the file
            data = f.read()
        if decompiled:
            if extension == "bin":
                data = data.decode("utf-8")
                scene = Scene(data, "text")
                data = scene.get_binary()
        return data

    def create_packfile(self, paths, filetypes, out_path):
        print(len(paths), len(filetypes))
        pack_json = {}
        pack_json["version"] = 2
        pack_json["order"] = paths
        pack_json["files"] = {}
        for i in range(len(paths)):
            path = paths[i]
            filetype = filetypes[i]
            data = self.get_file_bytes(path)
            if self.check_if_filetype_is_compressed(filetype):
                data = zlib.compress(data)
            pack_json["files"][path] = {
                "data": data,
                "type": filetype,
                "compress": self.check_if_filetype_is_compressed(filetype)
            }
        packfile = Packfile(pack_json, "json")
        with open(out_path, "wb") as f:
            f.write(packfile.get_binary())

    def pack_from_scene(self, relative_path, packfiles_path):
        paths = []
        filetypes = []
        referenced_files = {}

        # open _dynamic.pak
        if not relative_path.lower().endswith("_dynamic.bin") and not relative_path.lower().endswith("_dynamic.bin.json"):
            with open(os.path.join(packfiles_path, "_dynamic.pak"), "rb") as f:
                dynamic_pak = Packfile(f.read())
                dynamic_pak_json = dynamic_pak.get_json()
                self.paths_to_exclude = dynamic_pak_json["order"]
        # open scene
        scene = None
        if relative_path.endswith(".bin"):
            scene = Scene(self.get_file_bytes(relative_path))
        elif relative_path.endswith(".bin.json"):
            scene = Scene(self.get_file_bytes(relative_path), "text")
        
        paths, filetypes = self.get_referenced_files_for_scene(relative_path)
        # add the scene to the beginning of the paths and filetypes
        paths.insert(0, relative_path)
        filetypes.insert(0, "")

        upper_filetypes = []
        for filetype in filetypes:
            upper_filetypes.append(filetype.upper())
        filetypes = upper_filetypes

        

        i = 0
        i_max = len(paths)
        while i < i_max:
            path = paths[i]
            filetype = filetypes[i]
            if path.endswith(".hkw"):
                # get the directory of the hkw
                directory = os.path.dirname(path)
                # loop through every file in the directory and subdirectories
                for root, _, filenames in os.walk(os.path.join(self.base_dir, directory)):
                    # if it ends with behaviorproject.hkx or behaviorproject.hkx_wii
                    for filename in filenames:
                        if filename.lower() == "behaviorproject.hkx" or filename.lower() == "behaviorproject.hkx_wii":
                            # add the hkx to the paths and filetypes
                            paths.append(os.path.join(root, filename).replace("\\", "/"))
                            filetypes.append("HKP")
                            i_max = len(paths)
                            i += 1
                        # if it ends with behavior.hkx or behavior.hkx_wii
                        elif filename.lower() == "behavior.hkx" or filename.lower() == "behavior.hkx_wii":
                            # add the hkx to the paths and filetypes
                            paths.append(os.path.join(root, filename).replace("\\", "/"))
                            filetypes.append("HKB")
                            i_max = len(paths)
                            i += 1
                        # if it ends with .hkw
                        elif filename.lower().endswith(".hkw"):
                            # add the hkx to the paths and filetypes
                            paths.append(os.path.join(root, filename).replace("\\", "/"))
                            filetypes.append("HKW")
                            i_max = len(paths)
                            i += 1
                        # if it ends with .hkx or .hkx_wii
                        elif filename.lower().endswith(".hkx") or filename.lower().endswith(".hkx_wii"):
                            # add the hkx to the paths and filetypes
                            paths.append(os.path.join(root, filename).replace("\\", "/"))
                            filetypes.append("HKX")
                            i_max = len(paths)
                            i += 1
            i_max = len(paths)
            i += 1
                        

        # get the filename for the relative path
        relative_path = relative_path.replace("\\", "/")
        filename = relative_path.split("/")[-1]
        # get the filename without the extension
        filename = filename.split(".")[0]
        # create the packfile name
        packfile_name = filename + ".pak"
        # create the packfile path
        packfile_path = os.path.join(packfiles_path, packfile_name)
        
        for i in range(len(paths)):
            paths[i] = paths[i].replace("\\", "/")
            filetypes[i] = filetypes[i].upper()
            path = paths[i]
            filetype = filetypes[i]
            if path.endswith(".nif_wii") or path.endswith(".nif"):
                # set the file type to nif
                filetypes[i] = "NIF"
        
        # remove any duplicates from the paths and filetypes arrays
        i = 0
        i_max = len(paths)
        while i < i_max:
            path = paths[i]
            filetype = filetypes[i]
            if paths.count(path) > 1 or path == "":
                # remove the path and filetype from the paths and filetypes arrays
                paths.pop(i)
                filetypes.pop(i)
                i -= 1
            i += 1
            i_max = len(paths)

        
        scenes_paths = []
        scenes_filetypes = []
        hkx_paths = []
        hkx_filetypes = []
        nif_paths = []
        nif_filetypes = []
        nif_textures_paths = []
        nif_textures_filetypes = []
        other_paths = []
        other_filetypes = []
        for path in paths:
            index = paths.index(path)
            filetype = filetypes[index]
            if path.endswith(".bin") or path.endswith(".bin.json") or path.lower().startswith("palettes"):
                scenes_paths.append(path)
                scenes_filetypes.append(filetype)
            elif filetype.lower() == "hkx":
                hkx_paths.append(path)
                hkx_filetypes.append(filetype)
            elif filetype.lower() == "nif":
                is_texture = False
                # open the nif and determine if it is a texture
                nif = NifFile.from_path(os.path.join(self.base_dir, path))
                for block in nif.blocks:
                    if block.__class__.__name__ == "NiSourceTexture":
                        if not block.file_name:
                            is_texture = True
                if is_texture:
                    nif_textures_paths.append(path)
                    nif_textures_filetypes.append(filetype)
                else:
                    nif_paths.append(path)
                    nif_filetypes.append(filetype)
            else:
                other_paths.append(path)
                other_filetypes.append(filetype)
        scenes_paths.append("Palettes/_Dynamic/PlayerTools/PaintStream.bin")
        scenes_filetypes.append("")
        scenes_paths.append("Palettes/_Dynamic/PlayerTools/ThinnerStream.bin")
        scenes_filetypes.append("")
        paths = []
        filetypes = []
        paths = scenes_paths + hkx_paths + nif_textures_paths + nif_paths + other_paths
        filetypes = scenes_filetypes + hkx_filetypes + nif_textures_filetypes + nif_filetypes + other_filetypes
        em2_proto = True
        # if em2 proto = true, remove palettes/_dynamic.bin from the paths and filetypes arrays
        if em2_proto is True:
            paths_to_remove = [
                "Palettes/_Dynamic/PlayerTools/PaintStream.bin",
                "Palettes/_Dynamic/PlayerTools/ThinnerStream.bin",
                "palettes/_Dynamic/Effects/PaintHit.bin",
                "palettes/_Dynamic/Effects/ThinnerHit.bin",
                "palettes/_Dynamic/Effects/MickeyThinnerDeathFX.bin"
            ]
            for i in range(len(paths_to_remove)):
                paths_to_remove[i] = paths_to_remove[i].replace("\\", "/")
                paths_to_remove[i] = paths_to_remove[i].lower()
            # remove all items from the paths and filetypes arrays that are in the paths_to_remove array
            i = 0
            i_max = len(paths)
            while i < i_max:
                path = paths[i]
                filetype = filetypes[i]
                if path.lower() in paths_to_remove:
                    # remove the path and filetype from the paths and filetypes arrays
                    paths.pop(i)
                    filetypes.pop(i)
                    # decrement i_max
                    i_max -= 1
                else:
                    i += 1



        self.create_packfile(paths, filetypes, packfile_path)
        packfile = None
        with open(packfile_path, "rb") as f:
            packfile = Packfile(f.read())
        packfile_json = packfile.get_json()
        order = packfile_json["order"]
        for path in order:
            print(path)