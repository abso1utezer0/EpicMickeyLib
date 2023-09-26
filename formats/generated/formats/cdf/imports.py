from importlib import import_module


type_module_name_map = {
	'Ubyte': 'generated.formats.cdf.basic',
	'Char': 'generated.formats.cdf.basic',
	'Littleuint32': 'generated.formats.cdf.basic',
	'FixedString': 'generated.formats.cdf.structs.FixedString',
	'ExportString': 'generated.formats.cdf.structs.ExportString',
	'SizedString': 'generated.formats.cdf.structs.SizedString',
	'FileObject': 'generated.formats.cdf.structs.FileObject',
	'Header': 'generated.formats.cdf.structs.Header',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
