import json
import os
import sys
import struct

from internal.filemanipulator import FileManipulator

class Scene:
    json_root = {}
    fm = None

    def __init__(self, data, format_type="binary", endian="big"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, endian)
            self.decompile()
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            raise Exception("Invalid format type specified.")
    
    def read_pointer(self):
        # read pointer
        pointer = self.fm.r_int()
        if self.json_root["version"] == 2:
            pointer += 4
        return pointer
    
    def read_pointed_string(self):
        # read pointer
        pointer = self.read_pointer()
        # read string
        string = self.fm.r_str_from_pointer(pointer)
        return string
    
    def read_property_data(self, class_name):
        data = None
        if class_name == "Float":
            data = self.fm.r_float()
        elif class_name == "Boolean":
            data = self.fm.r_bool()
        elif class_name == "String":
            data = self.read_pointed_string()
        elif class_name == "Point3":
            values = []
            for i in range(3):
                values.append(self.fm.r_float())
            data = (values[0], values[1], values[2])
        elif class_name == "Point2":
            values = []
            for i in range(2):
                values.append(self.fm.r_float())
            data = (values[0], values[1])
        elif class_name == "Matrix3":
            rows = []
            for i in range(3):
                values = []
                for i in range(3):
                    values.append(self.fm.r_float())
                rows.append((values[0], values[1], values[2]))
            data = (rows[0], rows[1], rows[2])
        elif class_name == "Integer":
            data = self.fm.r_int()
        elif class_name == "Entity Pointer":
            data = self.fm.r_int()
            if data == 0:
                data = None
        elif class_name == "Unsigned Short":
            data = self.fm.r_ushort()
        elif class_name == "Unsigned Integer":
            data = self.fm.r_int()
        elif class_name == "Color (RGB)":
            values = []
            for i in range(3):
                values.append(self.fm.r_float())
            data = (values[0], values[1], values[2])
        elif class_name == "Color (RGBA)":
            values = []
            for i in range(4):
                values.append(self.fm.r_float())
            data = (values[0], values[1], values[2], values[3])
        else:
            raise Exception("Unknown property class: " + class_name)
        return data

    def read_property(self):
        # add property element
        component_property = {}
        # read property name pointer
        name = self.read_pointed_string()
        # add name
        component_property["name"] = name
        # read property class pointer
        class_name = self.read_pointed_string()
        # add class
        component_property["class"] = class_name

        data_type_id = self.fm.r_int()
        data_type = None
        if data_type_id != 0:
            data_type = "unknown_" + str(data_type_id)
            if data_type_id == 1:
                data_type = "list"
            elif data_type_id == 2:
                data_type = "path"
            elif data_type_id == 3:
                data_type = "animation_path"
            elif data_type_id == 5:
                data_type = "palette_list"
        amount = self.fm.r_int()
        data = None
        if data_type == "list" or data_type == "palette_list":
            data = []
            for i in range(amount):
                data.append(self.read_property_data(class_name))
        elif amount == 1:
            data = self.read_property_data(class_name)
        elif amount == 0:
            data = None
        else:
            raise Exception("Unknown data type: " + data_type)
        component_property["data"] = data
        if data_type != None:
            component_property["type"] = data_type
        return component_property
    
    def read_component(self):
        # add component element
        component = {}
        
        class_name = self.read_pointed_string()
        component["class"] = class_name
        template_id = self.read_pointed_string()
        component["template_id"] = template_id
        link_id = self.fm.r_int()
        component["link_id"] = link_id
        master_link_id = self.fm.r_int()
        if master_link_id != 0:
            component["master_link_id"] = master_link_id
        property_amount = self.fm.r_int()
        component_properties = []
        for i in range(property_amount):
            component_property = self.read_property()
            component_properties.append(component_property)
        component["properties"] = component_properties
        return component
    
    def read_entity(self):
        entity = {}
        name = self.read_pointed_string()
        entity["name"] = name
        link_id = self.fm.r_int()
        entity["link_id"] = link_id
        master_link_id = self.fm.r_int()
        if master_link_id != 0:
            entity["master_link_id"] = master_link_id
        unknown = self.fm.r_int()
        if unknown != 0:
            entity["unknown"] = unknown
        if self.json_root["version"] == 2:
            unknown_em2 = self.fm.r_int()
            if unknown_em2 != 0:
                entity["unknown_em2"] = unknown_em2
        component_amount = self.fm.r_int()
        components = []
        for i in range(component_amount):
            component = self.read_component()
            components.append(component)
        entity["components"] = components
        return entity
    
    def read_entities(self, entity_amount):
        entities = []
        for i in range(entity_amount):
            entity = self.read_entity()
            entities.append(entity)
        return entities

    def read_scene(self, entity_amount):
        linked_entities = []
        for i in range(entity_amount):
            linked_entity = self.fm.r_int()
            linked_entities.append(linked_entity)
        return linked_entities
    
    def decompile(self):
        # read the first 4 bytes
        first_four_bytes = self.fm.r_bytes(4)
        # if they equal 01 00 00 01, then the file is of version 2
        if first_four_bytes == b"\x01\x00\x00\x01":
            self.json_root["version"] = 2
        else:
            self.json_root["version"] = 1
            self.fm.seek(0)
        
        # read data pointer
        data_pointer = self.read_pointer()
        self.fm.seek(data_pointer)

        if self.json_root["version"] == 1:
            unique_id = self.fm.r_bytes(16)
            unique_id = "".join([hex(byte)[2:] for byte in unique_id])
            # seperate each byte by a comma
            unique_id = ",".join(unique_id[i:i+2] for i in range(0, len(unique_id), 2))
            self.json_root["unique_id"] = unique_id
        else:
            self.fm.move(8)
            # read number of extra strings
            num_extra_strings = self.fm.r_int()
            em2_extra_strings = None
            if num_extra_strings > 0:
                # add "EM2EXTRASTRINGS" element
                em2_extra_strings = []
                # read extra strings
                for i in range(num_extra_strings):
                    em2_extra_strings.append(self.fm.r_next_str())
            self.json_root["em2_extra_strings"] = em2_extra_strings
        entity_amount = self.fm.r_int()
        linked_entity_amount = self.fm.r_int()
        entities = self.read_entities(entity_amount)
        linked_entities = self.read_scene(linked_entity_amount)
        self.json_root["entities"] = entities
        self.json_root["scene"] = linked_entities
    
    def get_referenced_files(self):
        referenced_files = {}
        for entity in self.json_root["entities"]:
            for component in entity["components"]:
                for component_property in component["properties"]:
                    # check if the "type" key exists
                    if not "type" in component_property:
                        continue
                    if component_property["type"] == "path" or component_property["type"] == "animation_path":
                        path = component_property["data"]
                        name = component_property["name"]
                        file_type = None
                        if name == "NIF File Path" or name == "DecalMaterialNifFile" or name == "Phantom NIF File":
                            file_type = "nif"
                        elif name == "Phantom HKX File" or name == "RB Hull File Path":
                            file_type = "hkx"
                        elif name == "Behavior File Path":
                            file_type = "hkp"
                        elif name == "Animation List Path":
                            file_type = "hkw"
                        elif name == "KFM File Path":
                            file_type = "kfm"
                        elif name == "Lua File Path":
                            file_type = ""
                        else:
                            raise Exception("Unknown path type: " + name)
                        if not path in referenced_files:
                            referenced_files[path] = file_type.upper()
        return referenced_files


    
    def get_json(self):
        return self.json_root
    
    def get_text(self):
        return json.dumps(self.json_root, indent=4)
    
    def get_binary(self):
        # TODO: implement
        return b""