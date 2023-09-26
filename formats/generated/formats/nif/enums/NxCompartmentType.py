from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class NxCompartmentType(BaseEnum):

	__name__ = 'NxCompartmentType'
	_storage = Uint

	SCT_RIGIDBODY = 0
	SCT_FLUID = 1
	SCT_CLOTH = 2
