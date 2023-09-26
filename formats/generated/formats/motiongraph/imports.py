from importlib import import_module


type_module_name_map = {
	'Byte': 'generated.formats.base.basic',
	'Ubyte': 'generated.formats.base.basic',
	'Uint64': 'generated.formats.base.basic',
	'Int64': 'generated.formats.base.basic',
	'Uint': 'generated.formats.base.basic',
	'Ushort': 'generated.formats.base.basic',
	'Int': 'generated.formats.base.basic',
	'Short': 'generated.formats.base.basic',
	'Char': 'generated.formats.base.basic',
	'Normshort': 'generated.formats.base.basic',
	'Rangeshort': 'generated.formats.base.basic',
	'Float': 'generated.formats.base.basic',
	'Double': 'generated.formats.base.basic',
	'Hfloat': 'generated.formats.base.basic',
	'ZString': 'generated.formats.base.basic',
	'ZStringBuffer': 'generated.formats.base.compounds.ZStringBuffer',
	'PadAlign': 'generated.formats.base.compounds.PadAlign',
	'FixedString': 'generated.formats.base.compounds.FixedString',
	'Vector2': 'generated.formats.base.compounds.Vector2',
	'Vector3': 'generated.formats.base.compounds.Vector3',
	'Vector4': 'generated.formats.base.compounds.Vector4',
	'Bool': 'generated.formats.ovl_base.basic',
	'OffsetString': 'generated.formats.ovl_base.basic',
	'Compression': 'generated.formats.ovl_base.enums.Compression',
	'VersionInfo': 'generated.formats.ovl_base.bitfields.VersionInfo',
	'Pointer': 'generated.formats.ovl_base.compounds.Pointer',
	'LookupPointer': 'generated.formats.ovl_base.compounds.LookupPointer',
	'ArrayPointer': 'generated.formats.ovl_base.compounds.ArrayPointer',
	'CondPointer': 'generated.formats.ovl_base.compounds.CondPointer',
	'ForEachPointer': 'generated.formats.ovl_base.compounds.ForEachPointer',
	'MemStruct': 'generated.formats.ovl_base.compounds.MemStruct',
	'SmartPadding': 'generated.formats.ovl_base.compounds.SmartPadding',
	'ZStringObfuscated': 'generated.formats.ovl_base.basic',
	'GenericHeader': 'generated.formats.ovl_base.compounds.GenericHeader',
	'Empty': 'generated.formats.ovl_base.compounds.Empty',
	'ZStringList': 'generated.formats.ovl_base.compounds.ZStringList',
	'MotiongraphHeader': 'generated.formats.motiongraph.compounds.MotiongraphHeader',
	'LuaModules': 'generated.formats.motiongraph.compounds.LuaModules',
	'MotiongraphRootFrag': 'generated.formats.motiongraph.compounds.MotiongraphRootFrag',
	'ActivityEntry': 'generated.formats.motiongraph.compounds.ActivityEntry',
	'Activities': 'generated.formats.motiongraph.compounds.Activities',
	'Activity': 'generated.formats.motiongraph.compounds.Activity',
	'MRFEntry1': 'generated.formats.motiongraph.compounds.MRFEntry1',
	'MRFArray1': 'generated.formats.motiongraph.compounds.MRFArray1',
	'MRFMember1': 'generated.formats.motiongraph.compounds.MRFMember1',
	'MRFEntry2': 'generated.formats.motiongraph.compounds.MRFEntry2',
	'MRFArray2': 'generated.formats.motiongraph.compounds.MRFArray2',
	'MRFMember2': 'generated.formats.motiongraph.compounds.MRFMember2',
	'Transition': 'generated.formats.motiongraph.compounds.Transition',
	'StateArray': 'generated.formats.motiongraph.compounds.StateArray',
	'TransStruct': 'generated.formats.motiongraph.compounds.TransStruct',
	'TransStructArray': 'generated.formats.motiongraph.compounds.TransStructArray',
	'MGTwo': 'generated.formats.motiongraph.compounds.MGTwo',
	'TransStructStop': 'generated.formats.motiongraph.compounds.TransStructStop',
	'TransStructStopList': 'generated.formats.motiongraph.compounds.TransStructStopList',
	'State': 'generated.formats.motiongraph.compounds.State',
	'XMLEntry': 'generated.formats.motiongraph.compounds.XMLEntry',
	'XMLArray': 'generated.formats.motiongraph.compounds.XMLArray',
	'AnimationFlags': 'generated.formats.motiongraph.bitstructs.AnimationFlags',
	'FloatInputData': 'generated.formats.motiongraph.compounds.FloatInputData',
	'SubCurveType': 'generated.formats.motiongraph.enums.SubCurveType',
	'CurveDataPoint': 'generated.formats.motiongraph.compounds.CurveDataPoint',
	'CurveDataPoints': 'generated.formats.motiongraph.compounds.CurveDataPoints',
	'CurveData': 'generated.formats.motiongraph.compounds.CurveData',
	'DataStreamResourceData': 'generated.formats.motiongraph.compounds.DataStreamResourceData',
	'DataStreamResourceDataPoints': 'generated.formats.motiongraph.compounds.DataStreamResourceDataPoints',
	'DataStreamResourceDataList': 'generated.formats.motiongraph.compounds.DataStreamResourceDataList',
	'AnimationActivityData': 'generated.formats.motiongraph.compounds.AnimationActivityData',
	'CoordinatedAnimationActivityData': 'generated.formats.motiongraph.compounds.CoordinatedAnimationActivityData',
	'ActivityAnimationInfo': 'generated.formats.motiongraph.compounds.ActivityAnimationInfo',
	'LoopedAnimationInfo': 'generated.formats.motiongraph.compounds.LoopedAnimationInfo',
	'RandomAnimationActivityData': 'generated.formats.motiongraph.compounds.RandomAnimationActivityData',
	'TurnFlags': 'generated.formats.motiongraph.bitstructs.TurnFlags',
	'TurnActivityData': 'generated.formats.motiongraph.compounds.TurnActivityData',
	'UseValueType': 'generated.formats.motiongraph.enums.UseValueType',
	'ForwardActivityData': 'generated.formats.motiongraph.compounds.ForwardActivityData',
	'RagdollPhysicsActivityFlags': 'generated.formats.motiongraph.bitstructs.RagdollPhysicsActivityFlags',
	'RagdollPhysicsActivityData': 'generated.formats.motiongraph.compounds.RagdollPhysicsActivityData',
	'BlendSpaceAxis': 'generated.formats.motiongraph.compounds.BlendSpaceAxis',
	'Locomotion2BlendSpace': 'generated.formats.motiongraph.compounds.Locomotion2BlendSpace',
	'Locomotion2ActivityData': 'generated.formats.motiongraph.compounds.Locomotion2ActivityData',
	'VariableBlendedAnimationData': 'generated.formats.motiongraph.compounds.VariableBlendedAnimationData',
	'HeadTargetActivityData': 'generated.formats.motiongraph.compounds.HeadTargetActivityData',
	'VariableBlendedAnimationActivityData': 'generated.formats.motiongraph.compounds.VariableBlendedAnimationActivityData',
	'Locomotion2AnimationInfo': 'generated.formats.motiongraph.compounds.Locomotion2AnimationInfo',
	'Locomotion2BlendSpaceNode': 'generated.formats.motiongraph.compounds.Locomotion2BlendSpaceNode',
	'FootPlantActivityData': 'generated.formats.motiongraph.compounds.FootPlantActivityData',
	'TimeLimitMode': 'generated.formats.motiongraph.enums.TimeLimitMode',
	'SelectActivityActivityMode': 'generated.formats.motiongraph.enums.SelectActivityActivityMode',
	'DataStreamProducerActivityData': 'generated.formats.motiongraph.compounds.DataStreamProducerActivityData',
	'ActivitiesLink': 'generated.formats.motiongraph.compounds.ActivitiesLink',
	'ActivitiesLinks': 'generated.formats.motiongraph.compounds.ActivitiesLinks',
	'SelectActivityActivityData': 'generated.formats.motiongraph.compounds.SelectActivityActivityData',
	'GroupedActivityActivityData': 'generated.formats.motiongraph.compounds.GroupedActivityActivityData',
	'RandomActivityActivityInfoData': 'generated.formats.motiongraph.compounds.RandomActivityActivityInfoData',
	'SinglePtr': 'generated.formats.motiongraph.compounds.SinglePtr',
	'PtrList': 'generated.formats.motiongraph.compounds.PtrList',
	'StateList': 'generated.formats.motiongraph.compounds.StateList',
	'TwoPtrFirst': 'generated.formats.motiongraph.compounds.TwoPtrFirst',
	'ThirdFrag': 'generated.formats.motiongraph.compounds.ThirdFrag',
	'Sixtyfour': 'generated.formats.motiongraph.compounds.Sixtyfour',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
