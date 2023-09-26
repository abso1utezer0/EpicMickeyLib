from generated.formats.nif.imports import name_type_map
from generated.formats.nif.niphysx.niobjects.NiPhysXRigidBodyDest import NiPhysXRigidBodyDest


class NiPhysXTransformDest(NiPhysXRigidBodyDest):

	"""
	Connects PhysX rigid body actors to a scene node.
	"""

	__name__ = 'NiPhysXTransformDest'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
