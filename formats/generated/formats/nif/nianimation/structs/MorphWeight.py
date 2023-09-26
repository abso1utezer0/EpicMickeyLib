from generated.base_struct import BaseStruct
from generated.formats.nif.imports import name_type_map


class MorphWeight(BaseStruct):

	__name__ = 'MorphWeight'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		self.weight = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'weight', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'weight', name_type_map['Float'], (0, None), (False, None)
