from generated.formats.nif.imports import name_type_map
from generated.formats.nif.nianimation.niobjects.NiInterpController import NiInterpController


class NiMorpherController(NiInterpController):

	"""
	Unknown! Used by Daoc.
	"""

	__name__ = 'NiMorpherController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# This controller's data.
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiMorphData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiMorphData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiMorphData']), (False, None)
