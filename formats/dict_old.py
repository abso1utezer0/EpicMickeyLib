import argparse
import json
import os
import sys
import unicodedata

# get first argument
parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to read")
args = parser.parse_args()

path = args.file

# setup reading shortcuts
endian = "little";

r_int = lambda file, length: int.from_bytes(file.read(length), byteorder=endian);

r_str = lambda file, length: file.read(length).decode("utf-8");
# r_str_null - read string until null byte, return string. ensure to decode multiple-byte characters
def r_str_null(file):
    # read string until null byte
    str = "";
    while True:
        byte = file.read(1);
        if byte == b"\x00":
            break;
        try:
            str += byte.decode("utf-8");
        except UnicodeDecodeError:
            # multiple-byte character
            # get the next 2 bytes
            byte2 = file.read(1);
            byte3 = file.read(1);
            # combine the bytes
            bytes = byte + byte2 + byte3;
            try:
                # decode the bytes using multiple-byte character encoding
                str += bytes.decode("utf-8");
            except UnicodeDecodeError:
                # unknown character - add its escaped unicode value
                str += "\\u" + byte.hex() + byte2.hex() + byte3.hex();
    return str;

r_bytes = lambda file, length: file.read(length);
move = lambda file, amount: file.seek(file.tell() + amount);

# setup writing shortcuts
w_int = lambda file, value, length: file.write(value.to_bytes(length, byteorder=endian));
w_str = lambda file, value, length: file.write(value.encode("utf-8"));
w_bytes = lambda file, value: file.write(value);

def w_str_null(file, value):
    # write string to file, ending with null byte
    # if the string contains a unicode escape sequence, write the bytes instead
    # check if the string contains a unicode escape sequence
    bytes = b"";
    for i in range(0, len(value)):
        if value[i] == "\\" and value[i+1] == "u":
            # unicode escape sequence
            # get the unicode value
            unicode_value = value[i+2:i+6];
            # convert the unicode value to bytes
            bytes += bytes.fromhex(unicode_value);
        else:
            # normal character
            bytes += value[i].encode("utf-8");
    # write the bytes to the file
    file.write(bytes);
    # write null byte
    file.write(b"\x00");
    print(bytes)


def decompile() :
    # decompile file to json
    with open(path, "rb") as dct:
        # read magic
        magic = r_str(dct, 4) # = "DICT"
        if magic != "DICT":
            print("Invalid magic")
            return
        # read version 1
        version1 = r_int(dct, 4) # = 8192
        if version1 != 8192:
            print("Invalid version 1")
            return
        # read translation revision
        translation_revision = r_int(dct, 4) # = ???
        if translation_revision == 0:
            print("Invalid translation revision number.")
            return
        # read version 2
        version2 = r_int(dct, 4) # = 19
        if version2 != 19:
            print("Invalid version 2")
            return
        # read line count
        line_count = r_int(dct, 4) # = ???
        if line_count == 0:
            print("Invalid line count.")
            return
        # move forward 4 bytes
        move(dct, 4)
        # read footer offset - current position + r_int(dct, 4) + 9
        footer_offset = dct.tell() + r_int(dct, 4) + 9
        # move forward 4 bytes
        move(dct, 4)
        json_data = {}
        lines = {}
        footer = {}
        # add translation revision to json data
        json_data["translation_revision"] = translation_revision

        print(footer_offset)
        current_data_offset = dct.tell()
        empty_lines = 0
        # read lines
        for i in range(line_count):
            # read line id
            line_id = r_int(dct, 4)
            # if line id is 0, it is an empty line. add it to the lines and continue
            if line_id == 0:
                lines["empty_line_" + str(empty_lines)] = "";
                # move forward 8 bytes
                move(dct, 8)
                empty_lines += 1
                continue
            # read line offset - current position + r_int(dct, 4) + 1
            line_offset = dct.tell() + r_int(dct, 4) + 1
            # read line zero
            line_zero = r_int(dct, 4)
            # set current data offset
            current_data_offset = dct.tell()
            # go to line offset
            dct.seek(line_offset)
            # read line - r_str_null(dct)
            line = r_str_null(dct)
            line_id = hex(line_id)
            # remove 0x from line id
            line_id = line_id[2:]
            # while the line id is less than 8 characters, add a 0 to the start
            while len(line_id) < 8:
                line_id = "0" + line_id
            # swap the endianness of the line id
            line_id = line_id[6:8] + line_id[4:6] + line_id[2:4] + line_id[0:2]


            lines[line_id] = line
            print(line_id, line_offset, line_zero, line)
            # go to current data offset
            dct.seek(current_data_offset)
        # add lines to json data
        json_data["lines"] = lines
        while dct.tell() < footer_offset:
            # read footer line offset - current position + r_int(dct, 4) + 1
            footer_line_offset = dct.tell() + r_int(dct, 4) + 1
            # read footer line id
            footer_line_id = r_int(dct, 4)
            # set current data offset
            current_data_offset = dct.tell()
            # go to footer line offset
            dct.seek(footer_line_offset)
            # read footer line - r_str_null(dct)
            footer_line = r_str_null(dct)
            print(footer_line_offset, footer_line_id, footer_line)
            footer[footer_line] = footer_line_id
            # go to current data offset
            dct.seek(current_data_offset)
        # add footer to json data
        json_data["footer"] = footer
        # write json data to file
        with open(os.path.splitext(path)[0] + ".json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

def compile() :
    # compile json to file
    with open(path, "r") as json_file:
        # read json data
        json_data = json.load(json_file)
        # get translation revision
        translation_revision = json_data["translation_revision"]
        # get lines
        lines = json_data["lines"]
        # get footer
        footer = json_data["footer"]
        # get line count
        line_count = len(lines)
        # get footer line count
        footer_line_count = len(footer)
        # end offset
        end_offset = (line_count * 12) + (footer_line_count * 8) - 1
        line_data_length = line_count * 12
        footer_data_length = footer_line_count * 8
        with open(os.path.splitext(path)[0] + "_recomp.dct", "wb") as dct:
            # write magic
            w_str(dct, "DICT", 4)
            # write version 1
            w_int(dct, 8192, 4)
            # write translation revision
            w_int(dct, translation_revision, 4)
            # write version 2
            w_int(dct, 19, 4)
            # write line count
            w_int(dct, line_count, 4)
            # write 1
            w_int(dct, 1, 4)
            # write end offset
            w_int(dct, end_offset, 4)
            # write 1
            w_int(dct, 1, 4)
            current_data_offset = dct.tell()
            current_line_offset = end_offset + 50
            # go to current line offset
            dct.seek(current_line_offset)
            # write null byte
            w_int(dct, 0, 1)
            # go to current data offset
            dct.seek(current_data_offset)
            # write lines
            for line_id in lines:
                # get the object
                #if line id begins with empty_line_, it is an empty line. write 0 3 times and continue
                if line_id.startswith("empty_line_"):
                    # write 0 3 times
                    w_int(dct, 0, 4)
                    w_int(dct, 0, 4)
                    w_int(dct, 0, 4)
                    continue
                # write line id as bytes
                w_bytes(dct, bytes.fromhex(line_id))
                line_id = lines[line_id]
                # write line offset
                w_int(dct, (current_line_offset - dct.tell() - 1), 4)
                # write line zero
                w_int(dct, 0, 4)
                current_data_offset = dct.tell()
                # go to current line offset
                dct.seek(current_line_offset)
                # write line
                w_str_null(dct, line_id)
                # set current line offset
                current_line_offset = dct.tell()
                # go to current data offset
                dct.seek(current_data_offset)
            # write footer
            for footer_line in footer:
                # write offset
                w_int(dct, current_line_offset - dct.tell() - 1, 4)
                # write id
                w_int(dct, footer[footer_line], 4)
                current_data_offset = dct.tell()
                # go to current line offset
                dct.seek(current_line_offset)
                # write line
                w_str_null(dct, footer_line)
                # set current line offset
                current_line_offset = dct.tell()
                # go to current data offset
                dct.seek(current_data_offset)
            # write data end bytes
            # DF FF FF FF
            w_bytes(dct, b"\xdf\xff\xff\xff")
            w_int(dct, 11, 4)
            w_int(dct, 12, 4)
            w_int(dct, 0, 4)



        print(translation_revision)
        

# if the path ends with .dct, decompile it
if path.endswith(".dct"):
    decompile()
elif path.endswith(".json"):
    compile()
