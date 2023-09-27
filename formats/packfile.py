import os
import sys
import struct
import zlib
import io

from internal.filemanipulator import FileManipulator

# create packfile class
class Packfile:

    fm = None

    json_root = {}

    def __init__(self, data, endian="auto"):
        self.fm = FileManipulator()
        self.fm.from_bytes(data, endian)
        self.decompile()
    
    def get_json(self):
        return self.json_root
    
    def get_binary(self, endian="big"):
        out_fm = FileManipulator()
        out_fm.from_bytes(b"", endian)

        # magic
        magic = "PAK "
        if endian == "big":
            out_fm.w_str(magic[::-1])
        else:
            out_fm.w_str(magic)
        
        # version
        out_fm.w_int(self.json_root["version"])

        # header zero
        out_fm.w_int(0)

        # header size
        header_size = 32
        out_fm.w_int(header_size)

        path_partition = b""

        filename_pointers = []
        folder_pointers = []
        used_filenames = {}
        used_folders = {}

        for path in self.json_root["order"]:
            # get the directory (everything before the last forward slash)
            directory = path[0:path.rfind("/")]
            # get the filename (everything after the last forward slash)
            filename = path[path.rfind("/") + 1:len(path)]
            # remove the last forward slash from the directory if it exists
            if directory[len(directory) - 1] == "/":
                directory = directory[0:len(directory) - 1]
            # if the directory is not in the used folders array, add the offset to the used folders array
            if directory not in used_folders:
                used_folders[directory] = len(path_partition)
                path_partition += directory.encode("utf-8")
                path_partition += b"\0"
            folder_pointers.append(used_folders[directory])
            # if the filename is not in the used filenames array, add the offset to the used filenames array
            if filename not in used_filenames:
                used_filenames[filename] = len(path_partition)
                path_partition += filename.encode("utf-8")
                path_partition += b"\0"
            filename_pointers.append(used_filenames[filename])
        
        # header data pointer
        data_pointer = header_size + len(path_partition) + (len(self.json_root["order"]) * 24)
        while data_pointer % 32 != 0:
            data_pointer += 1
        out_fm.w_int(data_pointer - header_size)
        
        # go to the header size
        out_fm.seek(header_size)

        # number of files
        out_fm.w_int(len(self.json_root["files"]))

        # loop through all the files
        for path in self.json_root["order"]:
            # get the file
            file = self.json_root["files"][path]
            # get the real file size
            real_file_size = len(file["data"])
            # get the compressed file size
            compressed_file_size = real_file_size
            if file["compress"] == True:
                # compress the file
                compressed_data = zlib.compress(file["data"], 6)
                compressed_file_size = len(compressed_data)
            # get the aligned file size
            aligned_file_size = compressed_file_size
            while aligned_file_size % 32 != 0:
                aligned_file_size += 1
            # get the folder pointer
            folder_pointer = folder_pointers[self.json_root["order"].index(path)]
            # get the file type
            file_type = file["type"]
            # get the file pointer
            file_pointer = filename_pointers[self.json_root["order"].index(path)]
            # write the header values
            out_fm.w_int(real_file_size)
            out_fm.w_int(compressed_file_size)
            out_fm.w_int(aligned_file_size)
            out_fm.w_int(folder_pointer)
            # while file type is less than 4 characters, add null bytes to the end
            while len(file_type) < 4:
                file_type += "\0"
            # write the file type
            out_fm.w_str(file_type)
            out_fm.w_int(file_pointer)
        
        # write the path partition
        out_fm.w_bytes(path_partition)

        # go to the header data pointer
        out_fm.seek(data_pointer)

        for path in self.json_root["order"]:
            # get the file
            file = self.json_root["files"][path]
            # get the data
            data = file["data"]
            if file["compress"] == True:
                # compress the data
                data = zlib.compress(data, 6)
            # while the data size is not a multiple of 32, add null bytes to the end
            while len(data) % 32 != 0:
                data += b"\0"
            # write the data
            out_fm.w_bytes(data)
        
        # return the binary data
        return out_fm.get_bytes()

    def close(self):
        self.fm.close()

    def decompile(self):
        magic = self.fm.r_str(4)
        if magic == "PAK ":
            self.fm.set_endian("little")
        elif magic == " KAP":
            self.fm.set_endian("big")
        
        version = self.fm.r_int()
        zero = self.fm.r_int()
        header_size = self.fm.r_int()
        data_pointer = self.fm.r_int()
        data_pointer += header_size
        current_data_positon = data_pointer
        self.fm.seek(header_size)
        num_files = self.fm.r_int()
        string_pointer = (num_files * 24) + header_size + 4
        current_header_position = header_size + 4
        
        self.json_root["version"] = version

        # go to current header position
        self.fm.file.seek(current_header_position)

        files = {}
        order = []

        # loop through all files
        for i in range(num_files):
            file = {}
            # get the real file size as a 4 byte int
            real_file_size = self.fm.r_int()
            # get the compressed file size as a 4 byte int
            compressed_file_size = self.fm.r_int()
            # get the aligned file size as a 4 byte int
            aligned_file_size = self.fm.r_int()
            
            # read the folder pointer as a 4 byte int
            folder_pointer = self.fm.r_int()
            # read the file type as a 4 byte string
            file_type = self.fm.r_str(4)
            # remove null bytes
            file_type = file_type.replace("\0", "")
            file["type"] = file_type
            # read the file pointer as a 4 byte int
            file_pointer = self.fm.r_int()

            # add the string pointer to the folder name pointer and the file name pointer
            folder_pointer += string_pointer
            file_pointer += string_pointer

            # set the current header position to the current position
            self.current_header_position = self.fm.file.tell()

            # go to the folder name pointer
            self.fm.file.seek(folder_pointer)
            # read the folder name as a null terminated string
            folder_name = self.fm.r_str_null()

            # go to the file name pointer
            self.fm.file.seek(file_pointer)
            # read the file name as a null terminated string
            file_name = self.fm.r_str_null()

            # combine the folder name and the file name
            path = folder_name + "/" + file_name

            # go to the current data position
            self.fm.file.seek(current_data_positon)

            # read the data
            data = self.fm.r_bytes(compressed_file_size)

            # if the file is compressed, decompress it
            if compressed_file_size != real_file_size:
                file["compress"] = True
                data = zlib.decompress(data)
            else:
                file["compress"] = False
            
            # write the data to the file
            file["data"] = data
            files[path] = file
            order.append(path)

            # add the aligned file size to the current data position
            current_data_positon += aligned_file_size

            # go to the current header position
            self.fm.seek(self.current_header_position)
        
        self.json_root["files"] = files
        self.json_root["order"] = order