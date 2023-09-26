from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class NxCombineMode(BaseEnum):

	__name__ = 'NxCombineMode'
	_storage = Uint

	AVERAGE = 0
	MIN = 1
	MULTIPLY = 2
	MAX = 3
