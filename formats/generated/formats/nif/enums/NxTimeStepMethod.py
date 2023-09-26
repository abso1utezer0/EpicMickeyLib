from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class NxTimeStepMethod(BaseEnum):

	__name__ = 'NxTimeStepMethod'
	_storage = Uint

	TIMESTEP_FIXED = 0
	TIMESTEP_VARIABLE = 1
	TIMESTEP_INHERIT = 2
