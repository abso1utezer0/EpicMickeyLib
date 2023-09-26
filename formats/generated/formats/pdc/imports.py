from importlib import import_module


type_module_name_map = {
	'Biguint32': 'generated.formats.pdc.basic',
	'Bigushort': 'generated.formats.pdc.basic',
	'Ubyte': 'generated.formats.pdc.basic',
	'Char': 'generated.formats.pdc.basic',
	'LineString': 'generated.formats.pdc.basic',
	'FixedString': 'generated.formats.pdc.structs.FixedString',
	'SizedString': 'generated.formats.pdc.structs.SizedString',
	'CharacterEntry': 'generated.formats.pdc.structs.CharacterEntry',
	'G2Pb': 'generated.formats.pdc.structs.G2Pb',
	'Index7Bytes': 'generated.formats.pdc.structs.Index7Bytes',
	'UshortArrayContainer': 'generated.formats.pdc.structs.UshortArrayContainer',
	'WordEntry': 'generated.formats.pdc.structs.WordEntry',
	'PDCWordList': 'generated.formats.pdc.structs.PDCWordList',
	'PDCFile': 'generated.formats.pdc.structs.PDCFile',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
