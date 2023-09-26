from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Byte


class BroadPhaseType(BaseEnum):

	__name__ = 'BroadPhaseType'
	_storage = Byte

	BROAD_PHASE_INVALID = 0
	BROAD_PHASE_ENTITY = 1
	BROAD_PHASE_PHANTOM = 2
	BROAD_PHASE_BORDER = 3
