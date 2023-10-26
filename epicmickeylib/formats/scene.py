import json

from epicmickeylib.internal.filemanipulator import FileManipulator

class Scene:

    """
    A class representing a scene file in Epic Mickey.

    Attributes:
    - fm (FileManipulator): A FileManipulator object.
    - json_root (dict): A dictionary containing the JSON data of the scene file.

    Methods:
    - __init__(self, data, format_type="binary"): Initializes the Scene object.
    - read_pointer(self): Reads a pointer from the file.
    - read_pointed_string(self): Reads a string from the file.
    - read_property_data(self, class_name): Reads property data from the file.
    - write_property_data(self, class_name, data): Writes property data to the file.
    - read_property(self): Reads a property from the file.
    - write_property(self, component_property, strings): Writes a property to the file.
    - read_component(self): Reads a component from the file.
    - write_component(self, component, strings): Writes a component to the file.
    - read_entity(self): Reads an entity from the file.
    - write_entity(self, entity, strings): Writes an entity to the file.
    - read_entities(self, entity_amount): Reads entities from the file.
    - write_entities(self, entities, strings): Writes entities to the file.
    - read_scene(self, entity_amount): Reads a scene from the file.
    - write_scene(self, linked_entities): Writes a scene to the file.
    - add_string(self, string, strings): Adds a string to the string table.
    - assemble_strings(self): Assembles the string table.
    - get_referenced_palettes(self): Returns a list of referenced palettes.
    - get_referenced_files(self): Returns a list of referenced files.
    - decompile(self): Decompiles the binary data of the Scene object.
    - get_binary(self): Returns the binary data of the compiled Scene object.
    - get_text(self): Returns the JSON data of the Scene object as a string.
    - get_json(self): Returns the JSON data of the Scene object as a dictionary.
    """

    json_root = {}
    fm = None

    def __init__(self, data, format_type="binary", endian="big") -> None:

        """
        Initializes a Scene object.

        Args:
        - data: the data to be used to initialize the object
        - format_type: the format of the data (binary, json, or text)
        - endian: the endian of the data (big or little)

        Returns:
        None
        """

        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, endian)
            self.decompile()
        elif format_type == "json":
            self.json_root = data
        elif format_type == "text":
            self.json_root = json.loads(data)
        else:
            raise ValueError(f"""
                Invalid format type specified: {format_type}. Must be 'binary', 'json', or 'text'.
            """)

    def read_pointer(self) -> int:

        """
        Reads a pointer from the file.

        Args:
        None

        Returns:
        The pointer as an integer.
        """

        # read pointer
        pointer = self.fm.r_int()
        if self.json_root["version"] == 2:
            pointer += 4
        return pointer

    def read_pointed_string(self) -> str:

        """
        Reads a string from the file.

        Args:
        None

        Returns:
        The string.
        """
        # read pointer
        pointer = self.read_pointer()
        # read string
        string = self.fm.r_str_from_pointer(pointer)
        return string

    def read_property_data(self, class_name) -> str:

        """
        Reads property data from the file.

        Args:
        - class_name: the class of the property

        Returns:
        None
        """
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
        elif class_name == "Unsigned Short":
            data = self.fm.r_ushort()
            self.fm.align(4)
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
            raise ValueError(f"Unknown property class: {class_name}")
        return data

    def write_property_data(self, class_name, data) -> None:

        """
        Writes property data to the file.

        Args:
        - class_name: the class of the property

        Returns:
        None
        """

        if class_name == "Float":
            self.fm.w_float(data)
        elif class_name == "Boolean":
            self.fm.w_bool(data)
        elif class_name == "String":
            self.fm.w_int(data)
        elif class_name == "Point3":
            for num in data:
                self.fm.w_float(num)
        elif class_name == "Point2":
            for num in data:
                self.fm.w_float(num)
        elif class_name == "Matrix3":
            for row in data:
                for num in row:
                    self.fm.w_float(num)
        elif class_name == "Integer":
            self.fm.w_int(data)
        elif class_name == "Entity Pointer":
            self.fm.w_int(data)
        elif class_name == "Unsigned Short":
            self.fm.w_ushort(data)
            # write CD CD
            self.fm.w_bytes(b"\xCD\xCD")
        elif class_name == "Unsigned Integer":
            self.fm.w_int(data)
        elif class_name == "Color (RGB)":
            for num in data:
                self.fm.w_float(num)
        elif class_name == "Color (RGBA)":
            for num in data:
                self.fm.w_float(num)
        else:
            raise ValueError(f"Unknown property class: {class_name}")

    def read_property(self) -> dict:

        """
        Reads a property from the file.

        Args:
        None

        Returns:
        A dictionary containing the property data.
        """

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
        if data_type == "list" or data_type == "palette_list" or data_type == "animation_path":
            data = []
            for i in range(amount):
                data.append(self.read_property_data(class_name))
        else:
            if amount == 1:
                data = self.read_property_data(class_name)
            elif amount == 0:
                data = None
            else:
                data = []
                for i in range(amount):
                    data.append(self.read_property_data(class_name))
        #else:
        #    raise Exception("Unknown data type: " + data_type)
        component_property["data"] = data
        if data_type is not None:
            component_property["type"] = data_type
        return component_property

    def write_property(self, component_property, strings) -> None:

        """
        Writes a property to the file.

        Args:
        - component_property: a dictionary containing the property data
        - strings: a dictionary containing the string table

        Returns:
        None
        """

        # write property name pointer
        name = component_property["name"]
        self.fm.w_int(strings[name])
        # write property class pointer
        class_name = component_property["class"]
        self.fm.w_int(strings[class_name])
        data_type = None
        if "type" in component_property:
            data_type = component_property["type"]
        data_type_id = 0
        if data_type == "list":
            data_type_id = 1
        elif data_type == "path":
            data_type_id = 2
        elif data_type == "animation_path":
            data_type_id = 3
        elif data_type == "palette_list":
            data_type_id = 5
        # catch unknown data types
        if data_type_id == 0 and data_type is not None:
            # get the number from the string
            data_type_id = int(data_type.split("_")[1])
        self.fm.w_int(data_type_id)
        data = component_property["data"]
        if data_type == "list" or data_type == "palette_list" or data_type == "animation_path":
            amount = len(data)
            self.fm.w_int(amount)
            for item in data:
                if class_name == "String":
                    item = strings[item]
                # write data
                self.write_property_data(class_name, item)
        else:
            if data is None:
                amount = 0
            else:
                amount = 1
            self.fm.w_int(amount)
            if amount == 1:
                if class_name == "String":
                    data = strings[data]
                # write data
                self.write_property_data(class_name, data)

    def read_component(self) -> dict:

        """
        Reads a component from the file.

        Args:
        None

        Returns:
        A dictionary containing the component data.
        """

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

    def write_component(self, component, strings) -> None:

        """
        Writes a component to the file.

        Args:
        - component: a dictionary containing the component data
        - strings: a dictionary containing the string table

        Returns:
        None
        """

        # write component class pointer
        class_name = component["class"]
        self.fm.w_int(strings[class_name])
        # write component template id pointer
        template_id = component["template_id"]
        self.fm.w_int(strings[template_id])
        # write link id
        link_id = component["link_id"]
        self.fm.w_int(link_id)
        # write master link id
        if "master_link_id" in component:
            master_link_id = component["master_link_id"]
            self.fm.w_int(master_link_id)
        else:
            self.fm.w_int(0)
        # write property amount
        property_amount = len(component["properties"])
        self.fm.w_int(property_amount)
        # write properties
        for component_property in component["properties"]:
            self.write_property(component_property, strings)

    def read_entity(self) -> dict:

        """
        Reads an entity from the file.

        Args:
        None

        Returns:
        A dictionary containing the entity data.
        """

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

    def write_entity(self, entity, strings) -> None:

        """
        Writes an entity to the file.

        Args:
        - entity: a dictionary containing the entity data
        - strings: a dictionary containing the string table

        Returns:
        None
        """

        # write entity name pointer
        name = entity["name"]
        self.fm.w_int(strings[name])
        # write link id
        link_id = entity["link_id"]
        self.fm.w_int(link_id)
        # write master link id
        if "master_link_id" in entity:
            master_link_id = entity["master_link_id"]
            self.fm.w_int(master_link_id)
        else:
            self.fm.w_int(0)
        # write unknown
        if "unknown" in entity:
            unknown = entity["unknown"]
            self.fm.w_int(unknown)
        else:
            self.fm.w_int(0)
        # write unknown_em2
        if self.json_root["version"] == 2:
            unknown_em2 = 0
            if "unknown_em2" in entity:
                unknown_em2 = entity["unknown_em2"]
            self.fm.w_int(unknown_em2)
        # write component amount
        component_amount = len(entity["components"])
        self.fm.w_int(component_amount)
        # write components
        for component in entity["components"]:
            self.write_component(component, strings)

    def read_entities(self, entity_amount) -> list:

        """
        Reads entities from the file.

        Args:
        - entity_amount: the amount of entities to read

        Returns:
        A list containing the entities.
        """

        entities = []
        for i in range(entity_amount):
            entity = self.read_entity()
            entities.append(entity)
        return entities

    def write_entities(self, entities, strings) -> None:

        """
        Writes entities to the file.

        Args:
        - entities: a list containing the entities
        - strings: a dictionary containing the string table

        Returns:
        None
        """

        # write entities
        for entity in entities:
            self.write_entity(entity, strings)

    def read_scene(self, entity_amount) -> list:

        """
        Reads the linked entities from the file.

        Args:
        - entity_amount: the amount of entities to read

        Returns:
        A list containing the linked entities' ids.
        """

        linked_entities = []
        for i in range(entity_amount):
            linked_entity = self.fm.r_int()
            linked_entities.append(linked_entity)
        return linked_entities

    def write_scene(self, linked_entities) -> None:

        """
        Writes the linked entities to the file.

        Args:
        - linked_entities: a list containing the linked entities' ids

        Returns:
        None
        """

        # write entities
        for linked_entity in linked_entities:
            self.fm.w_int(linked_entity)

    def add_string(self, string, strings) -> dict:

        """
        Adds a string to the string table.

        Args:
        - string: the string to add
        - strings: a dictionary containing the string table

        Returns:
        A dictionary containing the string table.
        """

        if not string in strings:
            location = self.fm.tell()
            if self.json_root["version"] == 2:
                location -= 4
            strings[string] = location
            self.fm.w_next_str(string)
        return strings

    def assemble_strings(self) -> dict:

        """
        Assembles the string table.

        Args:
        None

        Returns:
        A dictionary containing the string table.
        """

        strings = {}

        for entity in self.json_root["entities"]:

            strings = self.add_string(entity["name"], strings)

            for component in entity["components"]:

                strings = self.add_string(component["class"], strings)
                strings = self.add_string(component["template_id"], strings)

                for component_property in component["properties"]:

                    strings = self.add_string(component_property["name"], strings)
                    strings = self.add_string(component_property["class"], strings)

                    if component_property["class"] == "String":

                        data_type = None

                        if "type" in component_property:
                            data_type = component_property["type"]

                        if data_type in ["list", "palette_list", "animation_path"]:

                            for item in component_property["data"]:
                                strings = self.add_string(item, strings)

                        else:
                            strings = self.add_string(component_property["data"], strings)
        return strings

    def decompile(self) -> None:

        """
        Decompiles the binary data and converts it to a JSON object.

        Args:
        None

        Returns:
        None
        """

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
            string = ""
            for byte in unique_id:
                # convert to hex string, no 0x
                byte = hex(byte)
                # remove 0x if it exists
                if byte[0:2] == "0x":
                    byte = byte[2:len(byte)]
                # add 0 if the length is 1
                if len(byte) == 1:
                    byte = "0" + byte
                # add to string
                string += byte + ","
            # remove last comma
            string = string[0:len(string) - 1]
            # add unique id
            self.json_root["unique_id"] = string
        else:
            self.fm.move(4)
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
        entities = []
        linked_entities = []
        # if we are at the end of the file, return
        if not self.fm.tell() >= self.fm.size() + 4:
            entity_amount = self.fm.r_int()
            linked_entity_amount = self.fm.r_int()
            entities = self.read_entities(entity_amount)
            linked_entities = self.read_scene(linked_entity_amount)
        self.json_root["entities"] = entities
        self.json_root["scene"] = linked_entities

    def get_referenced_palettes(self) -> list:

        """
        Returns a list of referenced palettes' names.

        Args:
        None

        Returns:
        A list containing the referenced palettes.
        """

        referenced_palettes = []
        for entity in self.json_root["entities"]:
            for component in entity["components"]:
                for component_property in component["properties"]:
                    # check if the "type" key exists
                    if not "type" in component_property:
                        continue
                    if component_property["type"] == "palette_list":
                        palette_list = component_property["data"]
                        for palette in palette_list:
                            if not palette in referenced_palettes:
                                referenced_palettes.append(palette)
        return referenced_palettes

    def get_referenced_files(self) -> list:

        """
        Returns lists of referenced files' paths and types.

        Args:
        None

        Returns:
        - A list containing the referenced files' paths.
        - A list containing the referenced files' types.
        """

        paths = []
        file_types = []

        def add_path(path, file_type):
            if not path in paths:
                paths.append(path)
                file_types.append(file_type)

        for entity in self.json_root["entities"]:

            for component in entity["components"]:

                for component_property in component["properties"]:

                    # check if the "type" key exists
                    if not "type" in component_property:
                        continue

                    if component_property["type"] == "path":

                        path = component_property["data"]
                        name = component_property["name"]

                        file_type = None

                        if name in [
                            "NIF File Path",
                            "DecalMaterialNifFile",
                            "Phantom NIF File",
                            "Portrait"]:
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
                            raise ValueError(f"Unknown path type: {name}")
                        add_path(path, file_type.upper())

        return paths, file_types

    def get_json(self) -> dict:

        """
        Returns the JSON data of the Scene object as a dictionary.

        Args:
        None

        Returns:
        dict: the JSON data of the Scene object
        """

        return self.json_root

    def get_text(self) -> str:

        """
        Returns the JSON data of the Scene object as a string.

        Args:
        None

        Returns:
        str: the JSON data of the Scene object
        """

        return json.dumps(self.json_root, indent=4)

    def get_binary(self) -> bytes:

        """
        Compiles the Scene object to binary data.

        Args:
        None

        Returns:
        bytes: the binary data of the Scene object
        """

        self.fm = FileManipulator()
        self.fm.from_bytes(b"", "big")
        if self.json_root["version"] == 2:
            self.fm.w_bytes(b"\x01\x00\x00\x01")
        data_pointer_location = self.fm.tell()
        data_pointer = 0
        self.fm.w_int(0)
        strings = self.assemble_strings()
        data_pointer = self.fm.tell()
        if self.json_root["version"] == 2:
            data_pointer -= 4
        self.fm.seek(data_pointer_location)
        self.fm.w_int(data_pointer)
        self.fm.seek(data_pointer)
        if self.json_root["version"] == 1:
            # write unique id
            unique_id = self.json_root["unique_id"]
            unique_id = unique_id.split(",")
            unique_id = [int(byte, 16) for byte in unique_id]
            unique_id = bytes(unique_id)
            self.fm.w_bytes(unique_id)
        else:
            # write 02 00 00 02
            self.fm.w_bytes(b"\x02\x00\x00\x02")
            # get the number of extra strings
            num_extra_strings = 0
            if "em2_extra_strings" in self.json_root:
                num_extra_strings = len(self.json_root["em2_extra_strings"])
            self.fm.w_int(num_extra_strings)
            # write extra strings
            if num_extra_strings > 0:
                for extra_string in self.json_root["em2_extra_strings"]:
                    self.fm.w_next_str(extra_string)
        # write entity amount
        entity_amount = len(self.json_root["entities"])
        self.fm.w_int(entity_amount)
        # write linked entity amount
        linked_entity_amount = 0
        # check if scene has no elements
        if "scene" in self.json_root and len(self.json_root["scene"]) > 0:
            linked_entity_amount = len(self.json_root["scene"])
        self.fm.w_int(linked_entity_amount)
        # write entities
        self.write_entities(self.json_root["entities"], strings)
        # write scene
        if linked_entity_amount > 0:
            self.write_scene(self.json_root["scene"])
        #else:
        #    self.fm.w_int(0)
        # return bytes
        return self.fm.get_bytes()
