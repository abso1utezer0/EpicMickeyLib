from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Byte


class BhkCMSMatType(BaseEnum):

	"""
	hkpCompressedMeshShape::MaterialType
	"""

	__name__ = 'bhkCMSMatType'
	_storage = Byte


	# Chunk builder makes sure that only chunks with the same material are created.
	SINGLE_VALUE_PER_CHUNK = 1
