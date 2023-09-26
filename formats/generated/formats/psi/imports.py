from importlib import import_module


type_module_name_map = {
	'Biguint32': 'generated.formats.psi.basic',
	'Bigushort': 'generated.formats.psi.basic',
	'Ubyte': 'generated.formats.psi.basic',
	'Char': 'generated.formats.psi.basic',
	'LineString': 'generated.formats.psi.basic',
	'FixedString': 'generated.formats.psi.structs.FixedString',
	'SizedString': 'generated.formats.psi.structs.SizedString',
	'PhonemeRecord': 'generated.formats.psi.structs.PhonemeRecord',
	'SimilarPhonemeRecord': 'generated.formats.psi.structs.SimilarPhonemeRecord',
	'UnknownStruct': 'generated.formats.psi.structs.UnknownStruct',
	'Header': 'generated.formats.psi.structs.Header',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
