from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class AnimNoteType(BaseEnum):

	"""
	Anim note types.
	"""

	__name__ = 'AnimNoteType'
	_storage = Uint


	# ANT_INVALID
	ANT_INVALID = 0

	# ANT_GRABIK
	ANT_GRABIK = 1

	# ANT_LOOKIK
	ANT_LOOKIK = 2
