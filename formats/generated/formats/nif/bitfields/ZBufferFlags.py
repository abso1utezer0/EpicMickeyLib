from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Bool
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.TestFunction import TestFunction


class ZBufferFlags(BasicBitfield):

	"""
	Flags for NiZBufferProperty
	"""

	__name__ = 'ZBufferFlags'
	_storage = Ushort
	z_buffer_test = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	z_buffer_write = BitfieldMember(pos=1, mask=0x0002, return_type=Bool.from_value)
	test_func = BitfieldMember(pos=2, mask=0x003C, return_type=TestFunction.from_value)

	def set_defaults(self):
		pass
