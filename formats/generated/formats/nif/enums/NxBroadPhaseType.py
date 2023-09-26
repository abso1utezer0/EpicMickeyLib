from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class NxBroadPhaseType(BaseEnum):

	__name__ = 'NxBroadPhaseType'
	_storage = Uint

	BP_TYPE_SAP_SINGLE = 0
	BP_TYPE_SAP_MULTI = 1
