from generated.base_struct import BaseStruct
from generated.formats.nif.imports import name_type_map


class PhysXClothAttachmentPosition(BaseStruct):

	__name__ = 'PhysXClothAttachmentPosition'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertex_id = name_type_map['Uint'](self.context, 0, None)
		self.position = name_type_map['Vector3'](self.context, 0, None)
		self.flags = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertex_id', name_type_map['Uint'], (0, None), (False, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'flags', name_type_map['Uint'], (0, None), (False, None)
