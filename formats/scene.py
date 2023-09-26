import os
import io
import struct
import sys

from internal.filemanipulator import FileManipulator
#from formats.generated.formats.nif import NifFile
import xml.etree.ElementTree as ET                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
import xml.dom.minidom

class Scene:
    gsa = None
    endian = "big"
    fm = None
    version = 1

    def __init__(self, data, format_type="binary", endian="big"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, endian)
            # read the first 4 bytes
            first_four_bytes = self.fm.r_bytes(4)
            # check if the first four bytes are 01 00 00 01
            if first_four_bytes != b"\x01\x00\x00\x01":
                self.fm.move(-4)
            else:
                self.version = 2
            self.decompile()
            
        elif format_type == "ascii":
            # parse xml
            self.gsa = ET.fromstring(data)
            self.version = int(self.gsa.get("Major"))
        else:
            print("Unknown type: " + type)
            sys.exit(1)

    def read_string(self, pointer=-1):
        if pointer == -1:
            pointer = self.read_pointer()
        # save current pointer
        current_pointer = self.fm.tell()
        # go to string pointer
        self.fm.seek(pointer + 2)
        # read string
        string = self.fm.r_str_null()
        # go back to current pointer
        self.fm.seek(current_pointer)
        return string
    def create_list(self, array):
        string = ""
        for i in range(len(array)):
            string += str(array[i])
            if i != len(array) - 1:
                string += ", "
        return string
    def format_float(self, num):
        num = str(num).split(".")
        # if there is no decimal point
        if len(num) == 1:
            # add decimal point
            num.append("")
        # add zeros to the end of the decimal part
        num[1] += "0" * (16 - len(num[1]))
        # join number back together
        num = ".".join(num)
        return num
    def read_pointer(self):
        # read pointer
        pointer = self.fm.r_int()
        if self.version == 2:
            pointer += 4
        return pointer
    def read_property(self, object):
        # add property element
        property = ET.SubElement(object, "PROPERTY")
        # read property name pointer
        name_pointer = self.read_pointer()
        # read property name
        name = self.read_string(name_pointer)
        # add name
        property.set("Name", name)
        # read property class pointer
        class_pointer = self.read_pointer()
        # read property class
        class_name = self.read_string(class_pointer)
        # add class name
        property.set("Class", class_name)
        #move(file, 4)
        unknown_data = self.fm.r_int()
        if unknown_data != 0:
            property.set("Unknown1", str(unknown_data))
        amount = self.fm.r_int()
        #if amount == 0:
        #    # add empty text
        #    property.text = ""
        #    return
        if class_name == "Float":
            for i in range(amount):
                if amount == 1:
                    property.text = self.format_float(self.fm.r_float())
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = self.format_float(self.fm.r_float())
        elif class_name == "Boolean":
            for i in range(amount):
                data = self.fm.r_int()
                if data == 0:
                    data = "FALSE"
                else:
                    data = "TRUE"
                if amount == 1:
                    property.text = data
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = data
        elif class_name == "String":
            if amount == 0:
                # add empty text
                property.text = ""
                property.set("Null", "True")
                return
            for i in range(amount):
                string_pointer = self.read_pointer()
                string = self.read_string(string_pointer)
                if amount == 1:
                    property.text = string
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = string

        elif class_name == "Point3":
            for i in range(amount):
                values = []
                for i in range(3):
                    values.append(self.format_float(self.fm.r_float()))
                if amount == 1:
                    property.text = self.create_list(values)
                else:
                    item = ET.SubElement(property, "ITEM")
                    item.text = self.create_list(values)
        elif class_name == "Point2":
            for i in range(amount):
                values = []
                for i in range(2):
                    values.append(self.format_float(self.fm.r_float()))
                if amount == 1:
                    property.text = self.create_list(values)
                else:
                    item = ET.SubElement(property, "ITEM")
                    item.text = self.create_list(values)
        elif class_name == "Matrix3":
            rows = []
            for i in range(3):
                row = []
                for j in range(3):
                    num = self.format_float(self.fm.r_float())
                    row.append(num)
                rows.append(row)
            for row in rows:
                # add "ROW" element
                row_element = ET.SubElement(property, "ROW")
                # add row values
                row_element.text = self.create_list(row)
        elif class_name == "Integer":
            for i in range(amount):
                data = self.fm.r_int()
                if amount == 1:
                    property.text = str(data)
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = str(data)
        elif class_name == "Entity Pointer":
            for i in range(amount):
                data = self.fm.r_int()
                if amount == 1:
                    property.text = str(data)
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = str(data)
        elif class_name == "Unsigned Short":
            for i in range(amount):
                data = self.fm.r_ushort()
                self.fm.move(2)
                if amount == 1:
                    property.text = str(data)
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = str(data)
        elif class_name == "Unsigned Integer":
            for i in range(amount):
                data = self.fm.r_int()
                if amount == 1:
                    property.text = str(data)
                else:
                    # add "ITEM" element
                    item = ET.SubElement(property, "ITEM")
                    item.text = str(data)
        elif class_name == "Color (RGB)":
            for i in range(amount):
                values = []
                for i in range(3):
                    values.append(self.format_float(self.fm.r_float()))
                string = self.create_list(values)
                if amount == 1:
                    property.text = string
                else:
                    item = ET.SubElement(property, "ITEM")
                    item.text = string
        elif class_name == "Color (RGBA)":
            for i in range(amount):
                values = []
                for i in range(4):
                    values.append(self.format_float(self.fm.r_float()))
                string = self.create_list(values)
                if amount == 1:
                    property.text = string
                else:
                    item = ET.SubElement(property, "ITEM")
                    item.text = string
        else:
            print("Unknown class: " + class_name)
            print("Please report this error on the OpenEM Epic Mickey Modding Discord server: https://discord.gg/gFrXryz8Kf")
            print("Offset: " + hex(self.fm.tell()))
            # exit with error code
            sys.exit(1)

    def decompile(self, endian="big"):
        # create xml tree
        self.gsa = ET.Element("GSA")
        # add xml version
        self.gsa.set("Major", str(self.version))
        self.gsa.set("Minor", "0")
        self.gsa.set("Patch", "0")
        data_offset = self.fm.r_int()
        # go to data offset
        self.fm.seek(data_offset)
        if self.version == 1:
            id = self.fm.r_bytes(16)
            # convert to hex, no 0x
            id = "".join([hex(byte)[2:] for byte in id])
            # seperate each byte by a comma
            id = ",".join(id[i:i+2] for i in range(0, len(id), 2))
            # add id to xml tree
            self.gsa.set("UniqueID", id)
        elif self.version == 2:
            self.fm.move(8)
            # read number of extra strings
            num_extra_strings = self.fm.r_int()
            if num_extra_strings > 0:
                # add "EM2EXTRASTRINGS" element
                em2_extra_strings = ET.SubElement(self.gsa, "EM2EXTRASTRINGS")
                # read extra strings
                for i in range(num_extra_strings):
                    self.fm.move(2)
                    string = self.fm.r_str_null()
                    # align to 4 bytes
                    if self.fm.tell() % 4 != 0:
                        self.fm.move(4 - (self.fm.tell() % 4))
                    print(string)
                    # add "ITEM" element
                    item = ET.SubElement(em2_extra_strings, "ITEM")
                    # add string
                    item.text = string
        objects = ET.SubElement(self.gsa, "OBJECTS")
        amount_of_entities = self.fm.r_int()
        amount_of_linked_entities = self.fm.r_int()
        for i in range(amount_of_entities):
            entity = ET.SubElement(objects, "ENTITY")
            entity_name = self.read_string()
            entity.set("Name", entity_name)
            entity_link_id = self.fm.r_int()
            entity.set("LinkID", str(entity_link_id))
            entity_master_link_id = self.fm.r_int()
            if entity_master_link_id != 0:
                entity.set("MasterLinkID", str(entity_master_link_id))
            entity_unknown = self.fm.r_int()
            if self.version == 2:
                entity_unknown_em2 = self.fm.r_int()
                if entity_unknown_em2 != 0:
                    entity.set("EM2UnknownData", str(entity_unknown_em2))
            amount_of_components = self.fm.r_int()
            for j in range(amount_of_components):
                component = ET.SubElement(entity, "COMPONENT")
                component_class = self.read_string()
                component.set("Class", component_class)
                component_template_id = self.read_string()
                component.set("TemplateID", component_template_id)
                component_link_id = self.fm.r_int()
                component.set("LinkID", str(component_link_id))
                component_master_link_id = self.fm.r_int()
                if component_master_link_id != 0:
                    component.set("MasterLinkID", str(component_master_link_id))
                amount_of_properties = self.fm.r_int()
                for k in range(amount_of_properties):
                    self.read_property(component)
        if amount_of_linked_entities > 0:
            scenes = ET.SubElement(self.gsa, "SCENES")
            scene = ET.SubElement(scenes, "SCENE")
            for i in range(amount_of_linked_entities):
                entity = ET.SubElement(scene, "ENTITY")
                entity_ref_link_id = self.fm.r_int()
                entity.set("RefLinkID", str(entity_ref_link_id))
    
    def get_actual_asset_path(self, path, base_path):
        extension_suffixes = [
            "_wii",
            "_wiu",
            "_pcr",
            "_ps3"
        ]
        for suffix in extension_suffixes:
            new_path = path + suffix
            absolute_path = os.path.join(base_path, new_path)
            if os.path.exists(absolute_path):
                return new_path
        if os.path.exists(os.path.join(base_path, path)):
            return path
        else:
            return None
    
    def get_referenced_files_for_file(self, path, file_type, base_path):
        paths = []
        file_types = []
        if file_type == "Animation List File Path":
            folder = os.path.dirname(path)
            # open file
            with open(path, "r") as file:
                # read lines
                lines = file.readlines()
                # loop through lines
                for line in lines:
                    # remove newline
                    line = line.replace("\n", "")
                    # get the filename from the line without the extension
                    filename = os.path.splitext(os.path.basename(line))[0]
                    # if filename ends with BehaviorProject
                    if filename.lower().endswith("behaviorproject"):
                        absolute_path = os.path.join(folder, line)
                        if self.check_if_asset_exists(absolute_path):
                            paths.append(absolute_path)
                            file_types.append("HKP")
                    else:
                        # file is likely in the animations folder
                        absolute_path = os.path.join(folder, "Animations", line)
                        if self.check_if_asset_exists(absolute_path):
                            paths.append(absolute_path)
                            file_types.append("HKB")
                    

    def get_referenced_files(self, base_path):
        # create list
        paths = []
        file_types = []
        for entity in self.gsa.find("OBJECTS").findall("ENTITY"):
            for component in entity.findall("COMPONENT"):
                if component.get("Class") == "String" and component.get("Null") != "True":
                    name = component.get("Name")
                    text = component.find("PROPERTY").text
                    file_type = ""
                    if text == "" or text == None:
                        continue
                    if name == "NIF File Path":
                        file_type = "NIF"
                    elif name == "RB Hull File Path":
                        file_type = "HKX"
                    elif name == "Behavior File Path":
                        file_type = "HKX"
                    elif name == "Animation List File Path":
                        file_type = "HKW"
                    elif name == "Sequences":
                        file_type = "BSQ"
                    elif name == "Portrait":
                        file_type = "NIF"
                    elif name == "KFM File Path":
                        file_type = "KFM"
                    elif name == "KF File Path":
                        file_type = "KF"
                    elif name == "Phantom NIF File":
                        file_type = "NIF"
                    elif name == "Phantom HKX File":
                        file_type = "HKX"
                    else:
                        # continue if the file type is not supported
                        continue

                    # check if it has ITEM children
                    has_multiple = False
                    if component.find("PROPERTY").find("ITEM") != None:
                        has_multiple = True

                    if not has_multiple:
                        paths.append(text)
                        file_types.append(file_type)
                    else:
                        for item in component.find("PROPERTY").findall("ITEM"):
                            paths.append(item.text)
                            file_types.append(file_type)
        # check if the files exists
        for i in range(len(paths)):
            path = paths[i]
            file_type = file_types[i]
            absolute_path = self.get_actual_asset_path(path, base_path)
            if absolute_path == None:
                # remove the path and file type from the list
                paths.pop(i)
                file_types.pop(i)
                # decrement i
                i -= 1
                continue

    def save(self, path, binary=False, endian="big"):
        if binary == False:
            # create xml string
            xml_string = ET.tostring(self.gsa, encoding="utf-8", method="xml")
            # parse xml string
            parsed_xml = xml.dom.minidom.parseString(xml_string)
            # write xml to file
            with open(path, "w") as file:
                file.write(parsed_xml.toprettyxml())
        else:
            print("Saving as binary is not supported yet.")

    def get_ascii(self):
        # create xml string
        xml_string = ET.tostring(self.gsa, encoding="utf-8", method="xml")
        # parse xml string
        parsed_xml = xml.dom.minidom.parseString(xml_string)
        # return xml
        return parsed_xml.toprettyxml()
    
    def get_binary(self, endian="big"):
        # TODO: finish this
        return b""

    # print
    def print(self):
        # create xml string
        xml_string = ET.tostring(self.gsa, encoding="utf-8", method="xml")
        # parse xml string
        parsed_xml = xml.dom.minidom.parseString(xml_string)
        # print xml
        print(parsed_xml.toprettyxml())