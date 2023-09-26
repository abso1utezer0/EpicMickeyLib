from generated.base_struct import BaseStruct
from generated.formats.nif.imports import name_type_map


class BSTreadTransform(BaseStruct):

	"""
	Bethesda-specific class.
	"""

	__name__ = 'BSTreadTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)
		self.transform_1 = name_type_map['NiQuatTransform'](self.context, 0, None)
		self.transform_2 = name_type_map['NiQuatTransform'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'transform_1', name_type_map['NiQuatTransform'], (0, None), (False, None), (None, None)
		yield 'transform_2', name_type_map['NiQuatTransform'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'transform_1', name_type_map['NiQuatTransform'], (0, None), (False, None)
		yield 'transform_2', name_type_map['NiQuatTransform'], (0, None), (False, None)
