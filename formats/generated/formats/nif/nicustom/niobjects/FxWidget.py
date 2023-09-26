from generated.array import Array
from generated.formats.nif.imports import name_type_map
from generated.formats.nif.nimain.niobjects.NiNode import NiNode


class FxWidget(NiNode):

	"""
	Firaxis-specific UI widgets?
	"""

	__name__ = 'FxWidget'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_3 = name_type_map['Byte'](self.context, 0, None)
		self.unknown_292_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_3', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'unknown_292_bytes', Array, (0, None, (292,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_3', name_type_map['Byte'], (0, None), (False, None)
		yield 'unknown_292_bytes', Array, (0, None, (292,), name_type_map['Byte']), (False, None)
