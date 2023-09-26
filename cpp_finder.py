#!/usr/bin/env python3
import mmap
import os
from sys import argv

def check_pos(pos, check_string):
    fm.seek(pos)
    # move forward by the length of the string
    fm.move(len(check_string))
    # check if the next character is a null byte
    byte = fm.r_byte()
    print(byte)
    if byte != b'\x00' or byte.isalnum():
        return ""
    fm.move(-2)
    # go back until a null byte is found or a non alphanumeric (including '.', '_', and '-') character is found
    byte = fm.r_byte()
    while byte != b'\x00' and (byte.isalnum() or byte == b'.' or byte == b'_' or byte == b'-'):
        fm.move(-2)
        byte = fm.r_byte()
    
    string = fm.r_str_null()
    if len(string) > 3:
        return string
    else:
        return ""

# NOTE: important to use `b''` literals!
pattern = b'.cpp'

cpp_files = []
cpp_pos = []

with open(argv[1], "r+b") as fh:
    with mmap.mmap(fh.fileno(), 0) as mm:
        pos = -1
        while -1 != (pos := mm.find(pattern, pos + 1)):
            cpp_pos.append(pos)

from internal.filemanipulator import FileManipulator

fm = FileManipulator(argv[1])

for pos in cpp_pos:
    string = check_pos(pos, pattern)
    if string != "" and string not in cpp_files:
        cpp_files.append(string)

h_files = []
h_pos = []

pattern = b'.h'

with open(argv[1], "r+b") as fh:
    with mmap.mmap(fh.fileno(), 0) as mm:
        pos = -1
        while -1 != (pos := mm.find(pattern, pos + 1)):
            h_pos.append(pos)


    

for pos in h_pos:
    string = check_pos(pos, pattern)
    if string != "" and string not in h_files:
        h_files.append(string)

print("cpp files:")
for file in cpp_files:
    print(file)

print("h files:")
for file in h_files:
    print(file)

print(len(cpp_files) + len(h_files))

out_dir = "E:/JunctionPoint/Mickey/Game/Code/Core/"

files = cpp_files + h_files

for file in files:
    path = os.path.join(out_dir, file)
    # if directory doesn't exist, create it
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    # create the file
    with open(path, "w") as fh:
        fh.write("")
