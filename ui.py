import importlib
if "bpy" in locals():
    importlib.reload(operator)
    importlib.reload(preset)
else:

    from . import (operator, preset)
    
import bpy

from bpy.types import (
        Panel,
        )


class SCENE_PT_EAD_SETUP(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    bl_category = "BT Sculpt"
    bl_label = "BT Add Primitive"

    def draw(self, context):

        layout = self.layout
        row = layout.row()
        row.label(text="Add Object")
        row = layout.row()

        cylinder = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_CYLINDER', text="")
        cylinder.type = 'CYLINDER'
        cylinder.arg = "Add Cylinder - Hold Shift to add object to cursor location"

        cube = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_CUBE', text="")
        cube.type = 'CUBE'
        cube.arg = "Add Cube - Hold Shift to add object to cursor location"

        torus = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_TORUS', text="")
        torus.type = 'TORUS'
        torus.arg = "Add Torus - Hold Shift to add object to cursor location"

        cone = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_CONE', text="")
        cone.type = 'CONE'
        cone.arg = "Add Cone - Hold Shift to add object to cursor location"

        sphere = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_UVSPHERE', text="")
        sphere.type = 'SPHERE'
        sphere.arg = "Add UV Sphere - Hold Shift to add object to cursor location"

        sphere = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='SHADING_TEXTURE', text="")
        sphere.type = 'SPHERE_CUBE'
        sphere.arg = "Add Cube Sphere - Hold Shift to add object to cursor location"

        pipe = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='META_CAPSULE', text="")
        pipe.type = 'PIPE'
        pipe.arg = "Add Pipe - Hold Shift to add object to cursor location"

        capsule = row.operator(operator.SCENE_OT_BTSculpt_Add_ParametricPrimitive.bl_idname, icon='MESH_CAPSULE', text="")
        capsule.type = 'CAPSULE'
        capsule.arg = "Add Capsule - Hold Shift to add object to cursor location"

        if context.object:
            for gn_modifier in context.object.modifiers:


                ################ CURVE PANEL UI ####################
                # gn_modifier = context.object.modifiers.get('BT_GN_CURVE_MODIFIER')

                if 'BT_GN_CURVE_MODIFIER' in gn_modifier.name:
                    # panel_header, panel_body = layout.panel("")
                    ng = gn_modifier.node_group
                    shading_smooth = ng.interface.items_tree.get('Shading Smooth')
                    angle = ng.interface.items_tree.get('Angle')
                    # row = panel_header.row()
                    row = layout.row()
                    row.label(text=context.object.name+" parametric setup")
                    panel_header = None
                    panel_body = None
                    if ng:
                        row = layout.row(align=True)
                        row.menu(preset.OBJECT_MT_BT_CURVE_presets.__name__,
                                 text=preset.OBJECT_MT_BT_CURVE_presets.bl_label)
                        row.operator(preset.AddPresetBTCurve.bl_idname, text="", icon='ZOOM_IN')
                        row.operator(preset.AddPresetBTCurve.bl_idname, text="", icon='ZOOM_OUT').remove_active = True
                        for item in ng.interface.items_tree:

                            if item.item_type == "PANEL":
                                panel_header, panel_body = layout.panel("Parametric Primitive")

                                row = panel_header.row()
                                row.label(text=item.name)
                            # print(gn_modifier['Socket_13'])
                            if item.item_type == "SOCKET" and panel_header and panel_body:
                                if item.identifier in gn_modifier:

                                    ############## menu switch options #####################
                                    if gn_modifier['Socket_18'] == 1:  # STAR

                                        if item.identifier == 'Socket_19' or item.identifier == 'Socket_16' or item.identifier == 'Socket_17':
                                            continue
                                    if gn_modifier['Socket_18'] == 0:  # 'CIRCLE':
                                        if item.identifier == 'Socket_19':
                                            continue
                                    if gn_modifier['Socket_18'] > 1:  # 'HAIR1 ecc...':
                                        if item.identifier == 'Socket_4' or item.identifier == 'Socket_16' or item.identifier == 'Socket_17':
                                            continue
                                    if gn_modifier['Socket_13'] == 0:  # 'NGON':
                                        if item.identifier == 'Socket_2':
                                            continue
                                    if gn_modifier['Socket_13'] == 1:  # 'LOOPS':
                                        if item.identifier == 'Socket_20':
                                            continue
                                    if not gn_modifier['Socket_22']:  # 'LOOPS':
                                        if item.identifier == 'Socket_23':
                                            continue
                                    if shading_smooth and angle:
                                        if not gn_modifier[shading_smooth.identifier]:  # 'LOOPS':
                                            if item.identifier == angle.identifier:
                                                continue
                                    row = panel_body.row()

                                    if item.socket_type == "NodeSocketCollection":
                                        row.prop_search(gn_modifier, f'["{item.identifier}"]', bpy.data, "collections",
                                                        text=item.name)
                                    elif item.socket_type == "NodeSocketObject":
                                        row.prop_search(gn_modifier, f'["{item.identifier}"]', bpy.data, "objects",
                                                        text=item.name)
                                    else:
                                        row.prop(gn_modifier, property=f'["{item.identifier}"]', text=item.name)
                ################ MESH/MODIFIER PANEL UI ####################
                # gn_modifier = context.object.modifiers.get('BT_GN_MESH_PRIMITIVE')

                if (
                        'BT_GN_MESH_PRIMITIVE' in gn_modifier.name or
                        'BT_GN_MODIFIER' in gn_modifier.name or
                        'BT_GN_REV_MODIFIER' in gn_modifier.name
                ):

                    ng = gn_modifier.node_group
                    shading_smooth = ng.interface.items_tree.get('Shading Smooth')
                    angle = ng.interface.items_tree.get('Angle')
                    row = layout.row()
                    row.label(text=context.object.name + " parametric setup")
                    panel_header = None
                    panel_body = None
                    if ng:
                        for item in ng.interface.items_tree:

                            if item.item_type == "PANEL":
                                panel_header, panel_body = layout.panel("Parametric Primitive")

                                row = panel_header.row()
                                row.label(text=item.name)

                            if item.item_type == "SOCKET" and panel_header and panel_body:
                                if item.identifier in gn_modifier:

                                    if shading_smooth and angle:
                                        if not gn_modifier[shading_smooth.identifier]:  # 'LOOPS':
                                            if item.identifier == angle.identifier:
                                                continue

                                    row = panel_body.row()

                                    if item.socket_type == "NodeSocketCollection":
                                        row.prop_search(gn_modifier, f'["{item.identifier}"]', bpy.data,
                                                        "collections",
                                                        text=item.name)
                                    elif item.socket_type == "NodeSocketObject":
                                        row.prop_search(gn_modifier, f'["{item.identifier}"]', bpy.data,
                                                        "objects",
                                                        text=item.name)
                                    else:
                                        row.prop(gn_modifier, property=f'["{item.identifier}"]',
                                                 text=item.name)

        row = layout.row()
        row.operator(operator.SCENE_OT_BTSculpt_ConvertToMesh.bl_idname, text="✅ Convert To editable Mesh")
        if context.mode == 'EDIT_CURVE':
            row = layout.row()
            row.operator(operator.SCENE_OT_BTSculpt_ChangeMode.bl_idname, icon='KEY_RETURN', text="")
        else:
            row = layout.row()
            row.label(text="Draw Curves")
            row = layout.row()
            curve = row.operator(operator.SCENE_OT_BTSculpt_Add_Curve.bl_idname, icon='OUTLINER_OB_CURVES', text="")
            curve.type = 'BASIC'
            curve.arg = "Add a Drawing curve with different profile selection"

            revolution = row.operator(operator.SCENE_OT_BTSculpt_Modifier_CurveRevolution.bl_idname,
                                      icon='EXPERIMENTAL', text="")
            revolution.type = 'REVOLUTION'
            revolution.arg = "Draw a profile to create a profile for a vase, revolution on Z axis"


        ############ MODIFIERS ##################
        row = layout.row()
        row.label(text="Modifiers")
        row = layout.row()
        row.operator(operator.SCENE_OT_BTSculpt_ConvertCurveToMesh.bl_idname, icon='MOD_LINEART', text="")
        row.operator(operator.SCENE_OT_BTSculpt_Add_Mirror.bl_idname, icon='MOD_MIRROR', text="")
        row.operator(operator.SCENE_OT_BTSculpt_Add_Subdivision.bl_idname, icon='MOD_SUBSURF', text="")
        radial_array = row.operator(operator.SCENE_OT_BTSculpt_ARRAY.bl_idname, icon='PARTICLE_POINT', text="")
        radial_array.type = 'RADIAL_ARRAY'
        radial_array.arg = "Add radial Array from the active object"
        array = row.operator(operator.SCENE_OT_BTSculpt_ARRAY.bl_idname, icon='MOD_ARRAY', text="")
        array.type = 'ARRAY'
        array.arg = "Add Array from the active object"




                
                    
        
        
