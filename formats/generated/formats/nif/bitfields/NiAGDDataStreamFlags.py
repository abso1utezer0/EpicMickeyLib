from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Bool
from generated.formats.nif.basic import Byte
from generated.formats.nif.enums.AGDConsistencyType import AGDConsistencyType


class NiAGDDataStreamFlags(BasicBitfield):

	"""
	Flags for NiAGDDataStream
	"""

	__name__ = 'NiAGDDataStreamFlags'
	_storage = Byte
	keep = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	consistency_type = BitfieldMember(pos=1, mask=0x0006, return_type=AGDConsistencyType.from_value)

	def set_defaults(self):
		self.consistency_type = AGDConsistencyType.AGD_MUTABLE
