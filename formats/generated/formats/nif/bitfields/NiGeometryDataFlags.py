from generated.bitfield import BasicBitfield
from generated.bitfield import BitfieldMember
from generated.formats.nif.basic import Ushort
from generated.formats.nif.enums.NiNBTMethod import NiNBTMethod


class NiGeometryDataFlags(BasicBitfield):

	__name__ = 'NiGeometryDataFlags'
	_storage = Ushort
	num_uv_sets = BitfieldMember(pos=0, mask=0x003F, return_type=Ushort.from_value)
	havok_material = BitfieldMember(pos=6, mask=0x0FC0, return_type=Ushort.from_value)
	nbt_method = BitfieldMember(pos=12, mask=0xF000, return_type=NiNBTMethod.from_value)

	def set_defaults(self):
		pass
