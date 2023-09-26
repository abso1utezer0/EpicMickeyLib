from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.LightingMode import LightingMode
from generated.formats.nif.enums.SourceVertexMode import SourceVertexMode


class VertexColorFlags(BasicBitfield):

	"""
	Flags for NiVertexColorProperty
	"""

	__name__ = 'VertexColorFlags'
	_storage = Ushort
	color_mode = BitfieldMember(pos=0, mask=0x0007, return_type=Ushort.from_value)
	lighting_mode = BitfieldMember(pos=3, mask=0x0008, return_type=LightingMode.from_value)
	source_vertex_mode = BitfieldMember(pos=4, mask=0x0030, return_type=SourceVertexMode.from_value)

	def set_defaults(self):
		pass
