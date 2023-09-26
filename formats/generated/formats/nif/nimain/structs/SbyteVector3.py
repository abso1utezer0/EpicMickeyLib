import math

from generated.formats.nif.nimain.structs.Vector3 import Vector3
from generated.base_struct import StructMetaClass
import generated.formats.nif as NifFormat
from generated.base_struct import BaseStruct
from generated.formats.nif.imports import name_type_map


class SbyteVector3(Vector3,BaseStruct,  metaclass=StructMetaClass):

	"""
	A vector in 3D space (x,y,z).
	"""

	__name__ = 'SbyteVector3'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# First coordinate.
		self.x = name_type_map['Normsbyte'](self.context, 0, None)

		# Second coordinate.
		self.y = name_type_map['Normsbyte'](self.context, 0, None)

		# Third coordinate.
		self.z = name_type_map['Normsbyte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x', name_type_map['Normsbyte'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Normsbyte'], (0, None), (False, None), (None, None)
		yield 'z', name_type_map['Normsbyte'], (0, None), (False, None), (None, None)

	@staticmethod
	def _get_filtered_attribute_list(instance, include_abstract=True):
		yield 'x', name_type_map["Normsbyte"], (0, None), (False, None)
		yield 'y', name_type_map["Normsbyte"], (0, None), (False, None)
		yield 'z', name_type_map["Normsbyte"], (0, None), (False, None)

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Normsbyte"].validate_instance(instance.x)
		name_type_map["Normsbyte"].validate_instance(instance.y)
		name_type_map["Normsbyte"].validate_instance(instance.z)

