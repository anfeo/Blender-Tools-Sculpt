bl_info = {
    "name": "Blender Tools Sculpt",
    "author": "Alfonso Annarumma",
    "version": (0, 0, 8),
    "blender": (4, 5, 0),
    "location": "Toolshelf > Blender Tools Sculpt",
    "warning": "",
    "description": "Blender Tools Sculpt",
    "category": "Add Mesh",
}

import importlib

if "bpy" in locals(): 
    
    importlib.reload(ui)    

    importlib.reload(operator)
    importlib.reload(preset)
else:

    from . import (ui, operator,preset)

import bpy

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    CollectionProperty,
    BoolVectorProperty,
    PointerProperty,
    EnumProperty,

)
import shutil
import os
import time
def copy_presets_to_user():
    user_preset_dir = bpy.utils.user_resource('SCRIPTS', path="presets", create=True)

    target_dir = os.path.join(user_preset_dir, "btpreset", "gn_curve")
    source_dir = os.path.join(os.path.dirname(__file__), "btpreset", "gn_curve")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # time.sleep(3)
    for file in os.listdir(source_dir):
        src = os.path.join(source_dir, file)
        dst = os.path.join(target_dir, file)
        if not os.path.exists(dst):
            shutil.copy(src, dst)


class SCENE_PG_BTSculpt_Prop(PropertyGroup):

    last_sculpt_object: PointerProperty(type=bpy.types.Object)


classes = (
    SCENE_PG_BTSculpt_Prop,
    # operator.SCENE_OT_BTSculpt_Add_Primitive,
    operator.SCENE_OT_BTSculpt_Add_Mirror,
    operator.SCENE_OT_BTSculpt_Add_Curve,
    operator.SCENE_OT_BTSculpt_ChangeMode,
    operator.SCENE_OT_BTSculpt_CurveUseSmooth,
    operator.SCENE_OT_BTSculpt_ConvertCurveToMesh,
    operator.SCENE_OT_BTSculpt_Add_Subdivision,
    operator.SCENE_OT_BTSculpt_Add_Capsule,
    operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive,
    operator.SCENE_OT_BTSculpt_ConvertToMesh,
    operator.SCENE_OT_ImagesFromFolder,
    operator.SCENE_OT_BTSculpt_ARRAY,
    operator.SCENE_OT_BTSculpt_Modifier_CurveRevolution,

    preset.AddPresetBTCurve,
    preset.OBJECT_MT_BT_CURVE_presets,
    preset.SCENE_OT_BT_ExecutePreset,
    ui.SCENE_PT_EAD_SETUP,

)


def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.bt_sculpt_prop = PointerProperty(type=SCENE_PG_BTSculpt_Prop)

    copy_presets_to_user()

def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.bt_sculpt_prop


if __name__ == "__main__":

    register()
