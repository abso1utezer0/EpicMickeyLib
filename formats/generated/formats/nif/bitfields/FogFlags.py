from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Bool
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.FogFunction import FogFunction


class FogFlags(BasicBitfield):

	"""
	Flags for NiFogProperty
	"""

	__name__ = 'FogFlags'
	_storage = Ushort
	enable = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	fog_function = BitfieldMember(pos=1, mask=0x0006, return_type=FogFunction.from_value)

	def set_defaults(self):
		pass
