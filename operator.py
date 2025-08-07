import importlib
import os

if "bpy" in locals():
    importlib.reload(function)
    importlib.reload(primitive)
else:
    from . import (function, primitive)

import bpy

from bpy.types import (
        Operator,

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

PROFILES = [
    'BT_STAR_PROFILE',
    'BT_COLUMN_PROFILE',
    'BT_HAIR1_PROFILE',
]

from bpy.types import OperatorFileListElement

class SCENE_OT_BTSculpt_Add_Subdivision(Operator):
    """Add Subdivision"""
    bl_idname = "scene.btsculpt_add_subdivision"
    bl_label = "Add Subdivision"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(name="Type", default="")
    levels: IntProperty(name="Level", default=2)

    @classmethod
    def poll(cls, context):
        if context.object:
            if context.object.type == 'MESH' or context.object.type == 'CURVE':

                return context.mode == "OBJECT" or context.mode == "SCULPT" or context.mode == 'EDIT' or context.mode == 'EDIT_CURVE'
        return False

    def execute(self, context):
        obj = context.object
        if context.mode == "SCULPT":
            function.add_multires(obj, self.levels)

        if context.mode == "OBJECT" or context.mode == 'EDIT' or context.mode == 'EDIT_CURVE':
            function.add_subsurf(obj, self.levels)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "levels")


class SCENE_OT_BTSculpt_Add_Capsule(Operator):
    """Add Capsule for Sculpt"""
    bl_idname = "scene.btsculpt_add_capsule"
    bl_label = "Add Capsule"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(default='CAPSULE')
    radius: FloatProperty(name="Radius", default=0.5, min=0.0)
    height: FloatProperty(name="Height", default=2.5, min=0.0)
    segments: IntProperty(name="Segments", default=24)
    rings: IntProperty(name="Rings", default=8)
    subdivision: IntProperty(name="Subdivision", default=1)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" or context.mode == "SCULPT"

    def execute(self, context):
        if self.type == 'CAPSULE':
            primitive.create_capsule(self,"BT_Capsule")

        return {'FINISHED'}


class SCENE_OT_BTSculpt_ARRAY(Operator):
    """ARRAY MODIFIER"""
    bl_idname = "scene.btsculpt_radial_array"
    bl_label = "Array"
    bl_options = {'REGISTER', 'UNDO'}

    arg: bpy.props.StringProperty()
    type: StringProperty(default='CAPSULE')

    @classmethod
    def description(cls, context, properties):
        return properties.arg
    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" or context.mode == "SCULPT"

    def execute(self, context):

        function.add_gn_modifier(context.object, f'BT_{self.type}', mod_name='BT_GN_MODIFIER')

        return {'FINISHED'}

class SCENE_OT_BTSculpt_Add_ParametricPrimitive(Operator):
    """Add Parametric Primitive for Sculpt"""
    bl_idname = "scene.btsculpt_add_parametricprimitive"
    bl_label = "Parametric Primitive"
    bl_options = {'REGISTER', 'UNDO'}

    arg: bpy.props.StringProperty()
    type: StringProperty(default='CAPSULE')

    @classmethod
    def description(cls, context, properties):
        return properties.arg
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT" or context.mode == "SCULPT"

    def execute(self, context):
        function.add_empty_mesh(context, f"BT_{self.type}")

        # primitive.create_soft_cone(self, name="BT_SoftCone")
        function.add_gn_modifier(context.object, f'BT_PARAMETRIC_{self.type}', mod_name="BT_GN_MESH_PRIMITIVE")
        scale = context.scene.unit_settings.scale_length
        context.object.scale *= scale
        return {'FINISHED'}

# class SCENE_OT_BTSculpt_Add_Primitive(Operator):
#     """Add Primitive for Sculpt"""
#     bl_idname = "scene.btsculpt_add_primitive"
#     bl_label = "Add Primitive"
#     bl_options = {'REGISTER', 'UNDO'}
#
#     angle: FloatProperty(name="Angle", default=70.0, min=0.0, max=360.0, step=100)
#     crease: FloatProperty(name="Crease", default=0.8 , min=0.0, max=1.0, step=1)
#     subdivision: IntProperty(name="Subdivision", default=4)
#     type: StringProperty(name="Type", default="")
#
#     @classmethod
#     def poll(cls, context):
#
#         return context.mode == "OBJECT" or context.mode == "SCULPT"
#
#     def execute (self, context):
#
#         function.sculpt_mesh_add (self, context)
#
#         return {'FINISHED'}


class SCENE_OT_BTSculpt_Add_Curve(Operator):
    """Add Primitive for Sculpt"""
    bl_idname = "scene.btsculpt_add_curve"
    bl_label = "Add Curve"
    bl_options = {'REGISTER', 'UNDO'}

    arg: bpy.props.StringProperty()
    type: StringProperty(default='CAPSULE')

    @classmethod
    def description(cls, context, properties):
        return properties.arg
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT" or context.mode == "SCULPT"

    def execute(self, context):
        function.add_empty_curve(context)
        function.add_gn_modifier(context.object, f'BT_CURVE_{self.type}', mod_name='BT_GN_CURVE_MODIFIER')
        scale = context.scene.unit_settings.scale_length
        context.object.scale *= scale

        return {'FINISHED'}


class SCENE_OT_BTSculpt_Modifier_CurveRevolution(Operator):
    """Modifier Curve Revolution"""
    bl_idname = "scene.btsculpt_modifier_curve_revolution"
    bl_label = "Revolution"
    bl_options = {'REGISTER', 'UNDO'}

    arg: bpy.props.StringProperty()
    type: StringProperty(default='REVOLUTION')

    @classmethod
    def description(cls, context, properties):
        return properties.arg
    @classmethod
    def poll(cls, context):
        if context.object:
            for mod in context.object.modifiers:
                if 'BT_GN_REV_MODIFIER' in mod.name:
                    return False
        return context.mode == "OBJECT" or context.mode == "SCULPT"

    def execute(self, context):
        function.add_empty_curve(context)
        context.object.modifiers.new("BT_Revolution_Screw", type='SCREW')
        function.add_gn_modifier(context.object, f'BT_CURVE_{self.type}', mod_name='BT_GN_REV_MODIFIER')
        scale = context.scene.unit_settings.scale_length
        context.object.scale *= scale

        return {'FINISHED'}

class SCENE_OT_BTSculpt_ChangeMode(Operator):
    """Return To last sculpt object"""
    bl_idname = "scene.btsculpt_turn_change_mode"
    bl_label = "Change Mode"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(name="Type", default="")

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_CURVE'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')


        return {'FINISHED'}

class SCENE_OT_BTSculpt_CurveUseSmooth(Operator):
    """Use Smooth"""
    bl_idname = "scene.btsculpt_curve_shading"
    bl_label = "Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    smooth: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_CURVE'

    def execute(self, context):
        for spline in context.object.data.splines:
            spline.use_smooth = self.smooth


        return {'FINISHED'}


class SCENE_OT_BTSculpt_ConvertCurveToMesh(Operator):
    """Convert the curve in mesh"""
    bl_idname = "scene.btsculpt_convert_curve_to_mesh"
    bl_label = "Curve To Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    sculpt: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.object:
            return context.object.type == "CURVE"
        return False

    def execute(self, context):
        function.convert_curve_to_mesh(context.object)
        if self.sculpt:
            bpy.ops.object.mode_set(mode='SCULPT')

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sculpt")
        layout.label(text="After this operation you can't edit the curve")


class SCENE_OT_BTSculpt_ConvertToMesh(Operator):
    """Convert to mesh"""
    bl_idname = "scene.btsculpt_convert_to_mesh"
    bl_label = "Convert To Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    # smooth: BoolProperty(default=True)
    sculpt: BoolProperty(default=True)
    @classmethod
    def poll(cls, context):
        if context.object:
            return context.object.type == "MESH" or context.object.type == "CURVE"
        return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if self.sculpt:
            bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"sculpt")
        layout.label(text="After this operation you can't")
        layout.label(text="change the object parameter")

class SCENE_OT_BTSculpt_Add_Mirror(Operator):
    """Add Mirror modifier on X"""
    bl_idname = "scene.btsculpt_add_mirror"
    bl_label = "Add Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    clipping: BoolProperty(default=False,
                            name="Merge and clip at center"
                            )
    use_target: BoolProperty(default=False,
                              name="Use center Scene",
                              description="Add an empty at the center of the scene an use as target for the cenetr of the mirror")

    @classmethod
    def poll(cls, context):
        if context.object:
            if context.object.type == 'MESH' or context.object.type == 'CURVE':
                return True
        return False

    def execute(self, context):
        if self.use_target:
            function.add_mirror_with_target(self,context)
        else:
            function.add_mirror(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    def draw(self, context):
        layout = self.layout

        layout.prop(self,"use_target")
        layout.prop(self,"clipping")

        # layout.label(text="After this operation you can't edit the curve")

class SCENE_OT_ImagesFromFolder(Operator):
    bl_idname = "scene.btsculpt_laod_iamges"
    bl_label = "Load Images in Textures"
    bl_description = "Select a folder with images "
    bl_options = {'REGISTER', 'UNDO'}

    # Permette di selezionare più file
    files: CollectionProperty(
        name="File Paths",
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    directory: StringProperty(
        subtype='DIR_PATH',
        options={'HIDDEN'}
    )

    filter_glob: StringProperty(
        default="*.jpg;*.png;*.tga;*.webp;*.tiff;*.tif;*.jpeg;*.exr;*.psd",
        options={'HIDDEN'}
    )

    IMAGE_EXTENSION = bpy.path.extensions_image

    def execute(self, context):
        textures = bpy.data.textures
        images = bpy.data.images
        # Ottieni i percorsi completi dei file selezionati
        filepaths = [os.path.join(self.directory, f.name) for f in self.files]
        # Filtra solo immagini
        image_files = [f for f in filepaths if os.path.splitext(f)[1].lower() in self.IMAGE_EXTENSION]
        # Ordina alfabeticamente
        image_files.sort()
        if not image_files:
            self.report({'WARNING'}, "No image selected")
            return {'CANCELLED'}
        print(image_files)
        for file in image_files:
            print(file)
            texture = textures.new(os.path.basename(file), type='IMAGE')
            image = images.load(file)
            texture.image = image


        self.report({'INFO'}, f"Loaded {len(image_files)} images in textures.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}