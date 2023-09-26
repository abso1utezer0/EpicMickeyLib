from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.TexClampMode import TexClampMode
from generated.formats.nif.enums.TexFilterMode import TexFilterMode


class TexturingMapFlags(BasicBitfield):

	"""
	Flags for NiTexturingProperty
	"""

	__name__ = 'TexturingMapFlags'
	_storage = Ushort
	texture_index = BitfieldMember(pos=0, mask=0x00FF, return_type=Ushort.from_value)
	filter_mode = BitfieldMember(pos=8, mask=0x0F00, return_type=TexFilterMode.from_value)
	clamp_mode = BitfieldMember(pos=12, mask=0x3000, return_type=TexClampMode.from_value)

	def set_defaults(self):
		pass
