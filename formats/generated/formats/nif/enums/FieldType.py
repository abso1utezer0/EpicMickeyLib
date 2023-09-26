from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class FieldType(BaseEnum):

	"""
	The force field type.
	"""

	__name__ = 'FieldType'
	_storage = Uint


	# Wind (fixed direction)
	FIELD_WIND = 0

	# Point (fixed origin)
	FIELD_POINT = 1
