from generated.formats.nif.imports import name_type_map
from generated.formats.nif.nimain.niobjects.NiObject import NiObject


class BSMultiBound(NiObject):

	"""
	Bethesda-specific object.
	"""

	__name__ = 'BSMultiBound'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['BSMultiBoundData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Ref'], (0, name_type_map['BSMultiBoundData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BSMultiBoundData']), (False, None)
