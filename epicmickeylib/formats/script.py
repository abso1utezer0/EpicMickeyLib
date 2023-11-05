# import the lua decomp/comp tools
import os
import sys
from epicmickeylib.internal.filemanipulator import FileManipulator
import epicmickeylib.thirdparty.lparser as lparser
import epicmickeylib.thirdparty.lundump as lundump

class Script:
    fm = None
    text = None

    def __init__(self, data, format_type="binary") -> None:
        if format_type == "binary":
            self.fm = FileManipulator()
            self.fm.from_bytes(data, "little")
            self.decompile()
        elif format_type == "text":
            self.text = data
        else:
            raise ValueError("Invalid format type: " + format_type)
    
    def decompile(self):
        lc = lundump.LuaUndump()
        chunk = lc.loadBytes(self.fm.get_bytes())

        #lc.print_dissassembly()

        lp = lparser.LuaDecomp(chunk)

        #print("\n==== [[" + str(chunk.name) + "'s pseudo-code]] ====\n")
        #print(lp.getPseudoCode())

        self.text = lp.getPseudoCode()
    
    def get_text(self):
        return self.text
    
    def get_binary(self):
        # compile the text using the installed lua compiler
        with open(".temp.lua", "w") as f:
            f.write(self.text)
        # strip the debug info
        os.system("luac -o .temp.luac -s .temp.lua")
        with open(".temp.luac", "rb") as f:
            data = f.read()
        os.remove(".temp.lua")
        os.remove(".temp.luac")
        return data