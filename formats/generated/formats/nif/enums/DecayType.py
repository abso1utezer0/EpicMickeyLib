from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class DecayType(BaseEnum):

	"""
	Describes the decay function of bomb forces.
	"""

	__name__ = 'DecayType'
	_storage = Uint


	# No decay.
	DECAY_NONE = 0

	# Linear decay.
	DECAY_LINEAR = 1

	# Exponential decay.
	DECAY_EXPONENTIAL = 2
