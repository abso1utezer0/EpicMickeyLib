from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class ColliderType(BaseEnum):

	"""
	This is used by the Floodgate kernel to determine which NiPSColliderHelpers functions to call.
	"""

	__name__ = 'ColliderType'
	_storage = Uint

	COLLIDER_PLANAR = 0
	COLLIDER_SPHERICAL = 1
