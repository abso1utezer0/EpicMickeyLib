from epicmickeylib.internal.filemanipulator import FileManipulator
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import sys

class HKX:
    fm = None
    xml = None
    assetcc2_path = None
    hkxcmd_path = None

    def __init__(self, data, format_type="binary", hkxcmd_path = None, assetcc2_path = None) -> None:
        self.assetcc2_path = assetcc2_path
        self.hkxcmd_path = hkxcmd_path
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, "little")
            self.decompile()
        elif format_type == "xml":
            self.xml = data
        elif format_type == "text":
            self.xml = ET.fromstring(data)
        else:
            raise ValueError(f"Invalid format type specified: {format_type}. Must be 'binary', 'xml', or 'text'.")
    
    def set_assetcc2_path(self, path) -> None:
        self.assetcc2_path = path
    
    def set_hkxcmd_path(self, path) -> None:
        self.hkxcmd_path = path
    
    def flip_int(self) -> int:
        num = self.fm.r_int()
        self.fm.move(-4)
        self.fm.set_endian("little")
        self.fm.w_int(num)
        self.fm.set_endian("big")
        return num

    def flip_float(self) -> float:
        num = self.fm.r_float()
        self.fm.move(-4)
        self.fm.set_endian("little")
        self.fm.w_float(num)
        self.fm.set_endian("big")
        return num

    def flip_short(self) -> int:
        num = self.fm.r_short()
        self.fm.move(-2)
        self.fm.set_endian("little")
        self.fm.w_short(num)
        self.fm.set_endian("big")
        return num

    def flip_byte(self) -> int:
        num = self.fm.r_byte()
        self.fm.move(-1)
        self.fm.set_endian("little")
        self.fm.w_byte(num)
        self.fm.set_endian("big")
        return num

    def flip_ushort(self) -> int:
        num = self.fm.r_ushort()
        self.fm.move(-2)
        self.fm.set_endian("little")
        self.fm.w_ushort(num)
        self.fm.set_endian("big")
        return num
    
    def flip(self, type, iterations=1):
        num = None
        for i in range(iterations):
            if type == "int":
                num = self.flip_int()
            elif type == "float":
                num = self.flip_float()
            elif type == "short":
                num = self.flip_short()
            elif type == "byte":
                num = self.flip_byte()
            elif type == "ushort":
                num = self.flip_ushort()
            else:
                raise ValueError(f"Invalid type specified: {type}. Must be 'int', 'float', 'short', 'byte', or 'ushort'.")
        if iterations == 1:
            return num

    def swap_endian(self) -> None:
        self.fm.move(12)
        self.flip("int")
        self.fm.w_bytes(b"\x04\x01\x00\x01")
        self.flip("int", 2)
        self.fm.move(8)
        self.flip("int")
        self.fm.r_str_null() # string version
        self.fm.align(16)
        # header section defs
        for i in range(3):
            self.fm.r_str_null() # section name
            self.fm.align(16)
            self.fm.move(4)
            self.flip("int", 7)
        filetype = ""
        # header classnames
        classnames = []
        while True:
            # read byte, if its 0x00 or 0xFF, break
            byte = self.fm.r_byte()
            byte = int.from_bytes(byte, "big")
            self.fm.move(-1)
            if byte == 0x00 or byte == 0xFF:
                break
            self.flip("int")
            self.fm.move(1)
            classname = self.fm.r_str_null()
            classnames.append(classname)
        self.fm.align(16)
        if "hkaSkeleton" in classnames:
            filetype = "skel"
        elif "hkaAnimationBinding" in classnames:
            filetype = "anim"
        elif "hkbProjectData" in classnames:
            filetype = "behavior"
        elif "hkbCharacterData" in classnames:
            filetype = "character"
        else:
            raise ValueError("Unsupported hkx file type.")
        if filetype == "skel":
            self.flip("int", 10)
            for i in range(4):
                self.fm.r_str_null()
                self.fm.align(16)
            self.flip("int", 44)

            # get shorts amount
            shorts_amount = self.flip("int")

            self.flip("int", 15)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", shorts_amount)

            self.fm.align(16)

            for i in range(shorts_amount):
                self.flip("int", 2)

            for i in range(shorts_amount):
                self.fm.r_str_null()
                self.fm.align(16)
        elif filetype == "anim":
            self.flip("int", 10)
            for i in range(4):
                self.fm.r_str_null()
                self.fm.align(16)
            self.flip("int", 84)
            # find the "Tracker" string
            shorts_offset = self.fm.get_bytes().find(b"Tracker")
            loc = self.fm.tell()
            self.fm.seek(shorts_offset)
            # until a 0 is reached, move backwards
            while True:
                self.fm.move(-1)
                byte = self.fm.r_byte()
                if int.from_bytes(byte, "big") == 0:
                    break
                else:
                    self.fm.move(-1)
            shorts_offset = self.fm.tell() - 68 - 28
            self.fm.seek(loc)

            # until the offset, flip ints
            while self.fm.tell() < shorts_offset:
                self.flip("int")

            self.flip("int", 17)

            num_shorts = self.flip("int")

            self.flip("int", 2)

            num_shorts2 = self.flip("int")
            self.flip("int", 3)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", num_shorts)

            self.fm.align(16)
            self.flip("short", num_shorts2)

            self.fm.align(16)
        elif filetype == "behavior":
            self.flip("int", 12)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 42 * 2)

            
            for i in range(7):
                self.fm.r_str_null()
                self.fm.align(16)
            
            self.flip("short", 12 * 2)
            self.fm.r_str_null()
            self.fm.align(16)
            


            self.flip("short", 12 * 2)
            self.fm.r_str_null()
            self.fm.align(16)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 12 * 2)
            self.fm.r_str_null()
            self.fm.align(16)
            

            self.flip("short", 12 * 2)
            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 18 * 2)
            

            self.fm.r_str_null()
            self.fm.align(16)

            self.fm.r_str_null()
            self.fm.align(16)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 12 * 2)
            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 5 * 2)
            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 12 * 2)

            for i in range(5):
                self.fm.r_str_null()
                self.fm.align(16)
            
            self.flip("int", 48)
            

            for i in range(8):
                self.fm.r_str_null()
                self.fm.align(16)
            
            self.flip("short", 8 * 2)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("short", 12 * 2)
            
            for i in range(5):
                self.fm.r_str_null()
                self.fm.align(16)
            
            self.flip("int", 12)

            self.fm.r_str_null()
            self.fm.align(16)

            self.fm.move(24)

            self.fm.r_str_null()
            self.fm.align(16)

            self.flip("int", 12)

            self.fm.r_str_null()
            self.fm.align(16)

            self.fm.move(42)

            self.flip("short")
            self.fm.move(22)
            self.flip("short")
            self.flip("int")

            for i in range(3):
                self.fm.r_str_null()
                self.fm.align(16)
            
            
            self.flip("int", 163)

            for i in range(2):
                self.fm.r_str_null()
                self.fm.align(16)
            
            self.flip("int", 22)
            
            num_anims = self.flip("int")
            self.flip("int", 13)

            self.fm.r_str_null()
            self.fm.align(16)
            
            
            
            self.flip("int", 8 + num_anims)

            print(num_anims )

            for i in range(num_anims):
                byte = self.fm.r_byte()
                self.fm.move(-1)
                if int.from_bytes(byte, "big") == 0:
                    self.fm.move(1)
                self.fm.r_str_null()
            
            
            self.fm.align(16)
            
            for i in range(2):
                self.flip("int", 1)
                self.fm.r_str_null()
                self.fm.align(16)
            print(hex(self.fm.tell()))
        elif filetype == "character":
            print("character")
        # for the rest of the file, flip ints
        while self.fm.tell() < self.fm.size():
            self.flip("int")
    
    def fix_xml(self) -> None:
        # get root
        root = self.xml
        # get <hksection name="__data__">
        data_section = root.find("./hksection[@name='__data__']")
        # get <hkobject class="hkaSplineCompressedAnimation">
        spline_compressed_animation = data_section.find("./hkobject[@class='hkaSplineCompressedAnimation']")
        # set <hkparam name="endian">0</hkparam> to 1
        endian = spline_compressed_animation.find("./hkparam[@name='endian']")
        endian.text = "1"
        # get <hkparam name="data">
        data_element = spline_compressed_animation.find("./hkparam[@name='data']")
        data = data_element.text.split("\n")
        # remove the first 6 spaces from each line and the last space
        for i in range(len(data)):
            data[i] = data[i][4:]
            data[i] = data[i][:-1]
        # remove empty lines
        data = list(filter(None, data))
        new_data = []
        # loop through lines
        for line in data:
            # split by spaces
            line = line.split(" ")
            new_line = []
            # swap orders of every group of 4 (0, 0, 0, 1) to (1, 0, 0, 0)
            groups = []
            for i in range(0, len(line), 4):
                groups.append(line[i:i+4])
            for group in groups:
                new_group = []
                new_group.append(group[2])
                new_group.append(group[1])
                new_group.append(group[0])
                new_group.append(group[3])
                for item in new_group:
                    new_line.append(item)
            # join by spaces
            new_line = " ".join(new_line)
            # if its not the first line
            new_line = "\t\t\t\t" + new_line
            # add to new data
            new_data.append(new_line)
        # add new line to the beginning of the first line
        new_data[0] = "\n" + new_data[0]
        # join by newlines
        new_data = "\n".join(new_data)
        # set data_element text to new data
        data_element.text = new_data

    
    def decompile(self) -> None:
        self.fm.seek(0x11)
        endian_byte = self.fm.r_byte()
        endian_byte = int.from_bytes(endian_byte, "big")
        self.fm.seek(0)
        if endian_byte == 0x00:
            self.swap_endian()
        # save data to temp file
        temp_dir = os.path.dirname(os.path.realpath(__file__))
        hkx_path = os.path.join(temp_dir, "temp.hkx")
        xml_path = os.path.join(temp_dir, "temp.xml")
        with open(hkx_path, "wb") as f:
            f.write(self.fm.get_bytes())
        # run hkxcmd
        if self.hkxcmd_path == None:
            raise ValueError("hkxcmd path not specified.")
        # run hkxcmd, no echo
        if sys.platform == "win32":
            os.system(f"{self.hkxcmd_path} Convert -i {hkx_path} -o {xml_path} -v:XML -f SAVE_SERIALIZE_IGNORED_MEMBERS SAVE_WRITE_ATTRIBUTES")
        else:
            os.system(f"{self.hkxcmd_path} Convert -i {hkx_path} -o {xml_path} -v:XML -f SAVE_SERIALIZE_IGNORED_MEMBERS SAVE_WRITE_ATTRIBUTES > /dev/null 2>&1")
        # read xml
        with open(xml_path, "r") as f:
            self.xml = ET.fromstring(f.read())
        # delete temp files
        os.remove(hkx_path)
        os.remove(xml_path)
        if endian_byte == 0x00:
            self.fix_xml()

    
    def get_xml(self) -> str:
        return self.xml
    
    def get_text(self) -> str:
        return ET.tostring(self.xml, encoding="unicode")