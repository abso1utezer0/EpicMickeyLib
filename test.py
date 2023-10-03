from generated.formats.nif import NifFile
# import xml
import xml.etree.ElementTree as ET

path = "E:/SteamLibrary/steamapps/common/Disney Epic Mickey 2/UI/Concept_Art/BA_Courtyard_tex.nif"

nif = NifFile().from_path(path)
for block in nif.blocks:
    NifFile.to_xml_file(block, "test.xml")