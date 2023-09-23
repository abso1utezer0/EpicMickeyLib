from internal.filemanipulator import FileManipulator
import os
import sys

class BSQ:
    fm = None
    json_root = {}
    def __init__(self, data, format_type="binary"):
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, "big")
            self.decompile()
        elif format_type == "ascii":
            self.json_root = data
        else:
            print("Unknown type: " + type)
            sys.exit(1)
        
    def get_unknown(self, id):
        return "unknown_item_id" + str(id)
    def read_item(self, id=-1):
        self.fm.align(4)
        if id == -1:
            id = self.fm.r_ushort()
        data = {}
        type = ""
        print("ID", str(id))
        if id == 0:
            type = "dialog"
            first_4 = self.fm.r_int()
            print("FIRST 4", first_4)
            if first_4 == 67108864:
                self.fm.move(-4)
                data["unknown_str1"] = self.fm.r_next_str()
                data["speaker_name"] = self.fm.r_next_str()
                data["speaker_icon"] = self.fm.r_next_str()
                data["target_entity"] = self.fm.r_next_str()
                data["line"] = self.fm.r_next_str()
                data["unknown_str2"] = self.fm.r_next_str()
                data["unknown_str3"] = self.fm.r_next_str()
                data["sfx"] = self.fm.r_next_str()
                data["unknown_str4"] = self.fm.r_next_str()
                data["unknown_bool1"] = self.fm.r_bool()
        elif id == 1:
            type = "unknown_type_id_1"
        elif id == 2:
            type = "dialog_question"
            first_4 = self.fm.r_int()
            print("FIRST 4", first_4)
            if first_4 == 67108864:
                self.fm.move(-4)
                data["unknown_str1"] = self.fm.r_next_str()
                data["speaker_name"] = self.fm.r_next_str()
                data["speaker_icon"] = self.fm.r_next_str()
                data["line"] = self.fm.r_next_str()
                data["unknown_str2"] = self.fm.r_next_str()
                data["sfx"] = self.fm.r_next_str()
                data["unknown_str3"] = self.fm.r_next_str()
                data["unknown_bool1"] = self.fm.r_bool()
                self.fm.move(4)
                amount_of_options = self.fm.r_int()
                print(amount_of_options)
                choices = []
                for i in range(amount_of_options):
                    choice = {}
                    choice["choice_text"] = self.fm.r_next_str()
                    choice["choice"] = self.fm.r_next_str()
                    choices.append(choice)
                data["choices"] = choices
        elif id == 3:
            type = "unknown_type_id_3"
            data["unknown_str1"] = self.fm.r_next_str()
            data["unknown_short1"] = self.fm.r_ushort()
            data["unknown_short2"] = self.fm.r_ushort()
        elif id == 4:
            type = "unknown_type_id_4"
            data["unknown_str1"] = self.fm.r_next_str()
        elif id == 5:
            type = "unknown_type_id_5"
            data["unknown_str1"] = self.fm.r_next_str()
            data["unknown_str2"] = self.fm.r_next_str()
            data["unknown_str3"] = self.fm.r_next_str()
            data["unknown_bool1"] = self.fm.r_bool()
            data["unknown_bool2"] = self.fm.r_bool()
            data["unknown_bool3"] = self.fm.r_bool()
        elif id == 7:
            type = "unknown_type_id_7"
            data["unknown_str1"] = self.fm.r_next_str()
            data["unknown_str2"] = self.fm.r_next_str()
            data["unknown_str3"] = self.fm.r_next_str()
            data["unknown_bool1"] = self.fm.r_bool()
        elif id == 9:
            type = "scripting"
            data["answer_required"] = self.fm.r_next_str()
            data["text"] = self.fm.r_next_str()
        elif id == 10:
            type = "unknown_type_id_10"
            data["unknown_str1"] = self.fm.r_next_str()
        elif id == 11:
            type = "unknown_type_id_11"
        elif id == 12:
            type = "unknown_type_id_12"
            data["unknown_str1"] = self.fm.r_next_str()
            data["unknown_float1"] = self.fm.r_float()
        elif id == 16:
            type = "unknown_type_id_16"
        elif id == 17:
            type = "unknown_type_id_17"
        elif id == 99:
            type = "unknown_type_id_99"
        elif id == 157:
            type = "unknown_type_id_157"
        elif id == 193:
            type = "unknown_type_id_193"
        else:
            print("UNKNOWN ID OF " + str(id))
            print("OFFSET: ", self.fm.file.tell())
            return -1
        
        item = {}
        item["type"] = type
        item["data"] = data
        return item


    def decompile(self):
        self.json_root["version"] = self.fm.r_int()
        self.json_root["scope"] = self.fm.r_next_str()
        self.json_root["character"] = self.fm.r_next_str()
        self.json_root["area"] = self.fm.r_next_str()
        sequences = []
        num1 = self.fm.r_ushort()
        self.json_root["num1"] = num1
        num2 = self.fm.r_ushort()
        self.json_root["num2"] = num2
        
        sequence = []
        amount = self.fm.r_int()
        print("AMOUNT:", amount)
        for i in range(amount):
            data = self.read_item()
            if data == -1:
                break
            else:
                sequence.append(data)
        self.json_root["sequence"] = sequence
        sequence2 = []
        for i in range(num2):
            data = self.read_item()
            if data == -1:
                break
            else:
                sequence2.append(data)
        self.json_root["sequence2"] = sequence2
        print("END OFFSET:", self.fm.file.tell())
    
    def compile(self):
        # TODO: Implement
        pass

    def get_binary(self):
        return self.compile()

    def get_ascii(self):
        return self.json_root

    def __str__(self):
        return str(self.json_root)