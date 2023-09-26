from generated.base_enum import BaseEnum
from generated.formats.nif.basic import Uint


class NiSceneDescNxHwPipelineSpec(BaseEnum):

	__name__ = 'NiSceneDescNxHwPipelineSpec'
	_storage = Uint

	RB_PIPELINE_HLP_ONLY = 0
	PIPELINE_FULL = 1
	PIPELINE_DEBUG = 2
