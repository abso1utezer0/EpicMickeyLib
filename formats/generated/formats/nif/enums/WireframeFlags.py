from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Ushort


class WireframeFlags(BaseEnum):

	"""
	Flags for NiWireframeProperty
	"""

	__name__ = 'WireframeFlags'
	_storage = Ushort

	WIREFRAME_DISABLED = 0
	WIREFRAME_ENABLED = 1
