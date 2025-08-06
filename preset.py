import bpy
from bpy.types import Operator, Menu
from bl_operators.presets import AddPresetBase
from bpy.props import (
        StringProperty,
)
from bpy.app.translations import (
    pgettext_rpt as rpt_,
    pgettext_data as data_,
)

def _call_preset_cb(fn, context, filepath, *, deprecated="4.2"):
    # Allow "None" so the caller doesn't have to assign a variable and check it.
    if fn is None:
        return

    if hasattr(fn, "__self__"):
        args_offset = 1
    else:
        args_offset = 0

    # Support a `filepath` argument, optional for backwards compatibility.
    fn_arg_count = getattr(getattr(fn, "__code__", None), "co_argcount", None)
    if fn_arg_count == 2 + args_offset:
        args = (context, filepath)
    else:
        print("Deprecated since Blender {:s}, a filepath argument should be included in: {!r}".format(deprecated, fn))
        args = (context, )

    try:
        fn(*args)
    except Exception as ex:
        print("Internal error running", fn, str(ex))


def _is_path_readonly(path):
    from bpy.utils import (
        is_path_builtin,
        is_path_extension,
    )
    # Consider extension repository paths read-only because they should not be manipulated
    # since the only way to restore the preset is to re-install the extension.
    return is_path_builtin(path) or is_path_extension(path)

class OBJECT_MT_BT_CURVE_presets(Menu):
    bl_label = "BT Curve Presets"
    preset_subdir = "btpreset/gn_curve"
    preset_operator = "script.bt_execute_preset"
    draw = Menu.draw_preset

class SCENE_OT_BT_ExecutePreset(Operator):
    """Load a preset"""
    bl_idname = "script.bt_execute_preset"
    bl_label = "Execute a Python Preset"

    filepath: StringProperty(
        subtype='FILE_PATH',
        options={'SKIP_SAVE'},
    )
    menu_idname: StringProperty(
        name="Menu ID Name",
        description="ID name of the menu this was called from",
        options={'SKIP_SAVE'},
    )

    def execute(self, context):

        gn_modifier = context.object.modifiers.get('BT_GN_CURVE_MODIFIER')
        print("Preset aggiunto")
        if gn_modifier:


            from os.path import basename, splitext
            filepath = self.filepath

            # change the menu title to the most recently chosen option
            # preset_class = getattr(bpy.types, self.menu_idname)
            preset_class = getattr(bpy.types, 'OBJECT_MT_BT_CURVE_presets')
            preset_class.bl_label = bpy.path.display_name(basename(filepath), title_case=False)

            ext = splitext(filepath)[1].lower()

            if ext not in {".py", ".xml"}:
                self.report({'ERROR'}, rpt_("Unknown file type: {!r}").format(ext))
                return {'CANCELLED'}

            _call_preset_cb(getattr(preset_class, "reset_cb", None), context, filepath)

            if ext == ".py":
                try:
                    bpy.utils.execfile(filepath)
                except Exception as ex:
                    self.report({'ERROR'}, "Failed to execute the preset: " + repr(ex))

            elif ext == ".xml":
                import rna_xml
                preset_xml_map = preset_class.preset_xml_map
                preset_xml_secure_types = getattr(preset_class, "preset_xml_secure_types", None)

                rna_xml.xml_file_run(context, filepath, preset_xml_map, secure_types=preset_xml_secure_types)

            _call_preset_cb(getattr(preset_class, "post_cb", None), context, filepath)

            gn_modifier.node_group.interface_update(context)

        return {'FINISHED'}


class AddPresetBTCurve(AddPresetBase, Operator):
    '''Add a BT geometry nodes Preset'''
    bl_idname = "object.bt_gn_curve_preset_add"
    bl_label = "Add BT Curve Presets"
    preset_menu = "OBJECT_MT_BT_CURVE_presets"

    # Variable used for all preset values.
    preset_defines = [
        "gn_modifier = bpy.context.object.modifiers.get('BT_GN_CURVE_MODIFIER')"
    ]
    # try:
    #     gn_modifier = bpy.context.object.modifiers.get('BT_GN_MODIFIER')
    #     if gn_modifier:
    #         sckts = bpy.context.object.modifiers['BT_GN_MODIFIER'].items()
    #
    #         for sckt in sckts:
    #             if not 'attribute' in sckt[0]:
    #                 preset_values.append(f"gn_modifier['{sckt}']")
    # except:

        # # Properties to store in the preset.
    preset_values = [
        "gn_modifier['Socket_18']",
        "gn_modifier['Socket_4']",
        "gn_modifier['Socket_10']",
        "gn_modifier['Socket_6']",
        "gn_modifier['Socket_5']",
        "gn_modifier['Socket_7']",
        "gn_modifier['Socket_13']",
        "gn_modifier['Socket_11']",
        "gn_modifier['Socket_9']",
        "gn_modifier['Socket_8']",
        "gn_modifier['Socket_3']",
        "gn_modifier['Socket_16']",
        "gn_modifier['Socket_17']",
        "gn_modifier['Socket_2']",
        "gn_modifier['Socket_20']",
    ]

    # Where to store the preset.
    preset_subdir = "btpreset/gn_curve"

