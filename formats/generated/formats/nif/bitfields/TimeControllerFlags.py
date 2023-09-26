from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Bool
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.AnimType import AnimType
from generated.formats.nif.enums.CycleType import CycleType


class TimeControllerFlags(BasicBitfield):

	"""
	Flags for NiTimeController
	"""

	__name__ = 'TimeControllerFlags'
	_storage = Ushort
	anim_type = BitfieldMember(pos=0, mask=0x0001, return_type=AnimType.from_value)
	cycle_type = BitfieldMember(pos=1, mask=0x0006, return_type=CycleType.from_value)
	active = BitfieldMember(pos=3, mask=0x0008, return_type=Bool.from_value)
	play_backwards = BitfieldMember(pos=4, mask=0x0010, return_type=Bool.from_value)
	manager_controlled = BitfieldMember(pos=5, mask=0x0020, return_type=Bool.from_value)
	compute_scaled_time = BitfieldMember(pos=6, mask=0x0040, return_type=Bool.from_value)
	forced_update = BitfieldMember(pos=7, mask=0x0080, return_type=Bool.from_value)

	def set_defaults(self):
		self.cycle_type = CycleType.CYCLE_CLAMP
		self.active = True
		self.compute_scaled_time = True
