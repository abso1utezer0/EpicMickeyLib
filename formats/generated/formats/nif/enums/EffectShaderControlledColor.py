from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class EffectShaderControlledColor(BaseEnum):

	"""
	An unsigned 32-bit integer, describing which color in BSEffectShaderProperty to animate.
	"""

	__name__ = 'EffectShaderControlledColor'
	_storage = Uint


	# Emissive Color.
	EMISSIVE_COLOR = 0
