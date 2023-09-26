from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Ushort


class AnimType(BaseEnum):

	__name__ = 'AnimType'
	_storage = Ushort

	APP_TIME = 0
	APP_INIT = 1
