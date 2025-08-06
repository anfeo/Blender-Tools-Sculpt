import bpy
import bmesh
import math
import os


def get_curve_setup(type):
    low_poly_curve = {
        'use_fill_caps': True,
        'bevel_depth': 0.1 * bpy.context.scene.unit_settings.scale_length,
        'bevel_resolution': 0,
        'resolution_u': 1,
    }
    smooth_curve = {
        'use_fill_caps': True,
        'bevel_depth': 0.1 * bpy.context.scene.unit_settings.scale_length,
        'bevel_resolution': 4,
        'resolution_u': 12,
    }
    if type == 'low_poly_curve':
        return low_poly_curve
    if type == 'smooth_curve':
        return smooth_curve


def setup_curve(curve_data, data_dict):

    for data in data_dict:
        setattr(curve_data, data, data_dict[data])


def get_gn_node(node_name):
    if node_name not in bpy.data.node_groups:
        filepath = os.path.join(os.path.dirname(__file__) + "/resources/", "nodes.blend")
        # if os.path.exists(filepath):
            # print(filepath)
        with bpy.data.libraries.load(filepath, relative=True) as (data_from, data_to):
            data_to.node_groups = [node_name]

    return bpy.data.node_groups[node_name]


def get_profile_curve(profile_name):
    if profile_name not in bpy.data.curves:
        filepath = os.path.join(os.path.dirname(__file__) + "/resources/", "curve_profiles.blend")
        with bpy.data.libraries.load(filepath, relative=True) as (data_from, data_to):
            data_to.curves = [profile_name]

    return bpy.data.curves[profile_name].copy()


def add_gn_modifier(obj, node_name, mod_name="BT_GN_MODIFIER"):
    # add remove double GN modifier
    gn = get_gn_node(node_name)
    gn_modifier = obj.modifiers.new(mod_name, type='NODES')
    gn_modifier.node_group = gn
    return gn_modifier

def add_subsurf(obj, levels):
    # add subdivision surface
    subsurf = obj.modifiers.new("BT_Subdivision", type='SUBSURF')
    subsurf.levels = levels


def add_multires(obj, levels):
    # add multires
    print(levels)
    multires = obj.modifiers.new("BT_Multires", type='MULTIRES')
    bpy.ops.object.multires_subdivide(modifier="BT_Multires", mode='CATMULL_CLARK')
    multires.levels = levels
    multires.sculpt_levels = levels


def setup_profile_curve(curve, profile_name):
    # curve = context.object
    smooth_curve = get_curve_setup("smooth_curve")
    setup_curve(curve.data, smooth_curve)
    data = get_profile_curve(profile_name)
    bpy.ops.object.mode_set(mode='OBJECT')
    curve.data = data
    bpy.ops.object.mode_set(mode='EDIT')
    add_gn_modifier(curve, "BT_Remove_Double")
    # add_subsurf(curve, levels=2)


def setup_spaghetti_curve(curve):

    smooth_curve = get_curve_setup("smooth_curve")
    setup_curve(curve.data, smooth_curve)

    # add_gn_modifier(curve, "BT_Remove_Double")
    add_subsurf(curve, levels=2)
    add_gn_modifier(curve, "BT_Remove_Double")


def setup_worm_curve(curve):
    # curve = context.object
    low_poly_curve = get_curve_setup("low_poly_curve")
    setup_curve(curve.data, low_poly_curve)

    add_gn_modifier(curve, "BT_Remove_Double")
    add_subsurf(curve, levels=2)


def convert_curve_to_mesh(curve):
    # check if there are subsurf
    subsurf_list = []
    levels = None
    for mod in curve.modifiers:
        if mod.type == "SUBSURF":
            subsurf_list.append(mod)
    if len(curve.modifiers) > 0:
        if curve.modifiers[0].type == "SUBSURF":
            levels = curve.modifiers[0].levels

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='MESH')
    # if levels:
    #     add_subsurf(bpy.context.object, levels)
    #     bpy.ops.object.convert(target='MESH')


def return_to_last_object(context):
    last_sculpt_object = context.scene.bt_sculpt_prop.last_sculpt_object
    if last_sculpt_object.type == 'MESH':
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = last_sculpt_object
        last_sculpt_object.select_set(True)
        bpy.ops.object.mode_set(mode='SCULPT')
    else:
        bpy.ops.object.mode_set(mode='OBJECT')


def add_empty_mesh(context, obj_name):

    if context.object:
        bpy.ops.object.mode_set(mode='OBJECT')
    # Crea una nuova curva (senza spline)
    mesh_data = bpy.data.meshes.new("BT_Mesh")

    # Crea l'oggetto
    mesh_object = bpy.data.objects.new(obj_name, mesh_data)
    context.collection.objects.link(mesh_object)

    # Rende l'oggetto attivo e selezionato
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = mesh_object
    mesh_object.select_set(True)


def add_empty_curve(context):

    context.scene.bt_sculpt_prop.last_sculpt_object = context.object
    if context.object:
        bpy.ops.object.mode_set(mode='OBJECT')
    # Crea una nuova curva (senza spline)
    curve_data = bpy.data.curves.new("NewCurve", type='CURVE')
    curve_data.dimensions = '3D'

    # Crea l'oggetto
    curve_object = bpy.data.objects.new("Curve", curve_data)
    context.collection.objects.link(curve_object)

    # Rende l'oggetto attivo e selezionato
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = curve_object
    curve_object.select_set(True)

    # Passa in modalità Edit
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.wm.tool_set_by_id(name="builtin.draw")
    context.tool_settings.curve_paint_settings.depth_mode = 'SURFACE'
    context.tool_settings.curve_paint_settings.use_pressure_radius = True


def add_empty():
    # Crea l'oggetto
    if "BT_Mirror_Emp" in bpy.data.objects:
        empity_object = bpy.data.objects["BT_Mirror_Emp"]
    else:
        empity_object = bpy.data.objects.new("BT_Mirror_Emp", None)
    # context.collection.objects.link(empity_object)

    return empity_object


def add_mirror_with_target(self,context):
    active = context.object
    target = add_empty()
    mirror = active.modifiers.new("mirror", type='MIRROR')
    mirror.mirror_object = target
    mirror.use_clip = self.clipping


def add_mirror(self,context):

    mirror = context.object.modifiers.new("mirror", type='MIRROR')
    mirror.use_clip = self.clipping


def add_primitive(self,context,type):
    cursor = context.scene.cursor.location

    if type == 'SPHERE_CUBE':
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location= cursor,
                                        scale=(1, 1, 1))
        sub = bpy.context.object.modifiers.new("subsurf", type='SUBSURF')
        sub.levels = self.subdivision
        bpy.context.object.modifiers.new("cast",type='CAST')
        bpy.ops.object.convert(target='MESH')
    if type == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add(end_fill_type='TRIFAN', enter_editmode=True, align='WORLD',
                                            location=cursor,
                                            scale=(1, 1, 1))

    if type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=True, align='WORLD', location=cursor,
                                        scale=(1, 1, 1))

    if type == 'TORUS':
        bpy.ops.mesh.primitive_torus_add(align='WORLD', location=cursor, rotation=(0, 0, 0), major_radius=1,
                                         minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75,  major_segments=24, minor_segments=6)
        sub = bpy.context.object.modifiers.new("subsurf", type='SUBSURF')
        sub.levels = self.subdivision

        bpy.ops.object.convert(target='MESH')
    if type == 'CONE':
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, enter_editmode=True, align='WORLD',
                                        location=cursor, scale=(1, 1, 1))

    if type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=True, align='WORLD', location=cursor,
                                             scale=(1, 1, 1))

    return bpy.context.object.data


def sculpt_mesh_add (self,context):
    # Get the active mesh
    me = add_primitive(self,context,self.type)
    if self.type == 'SPHERE_CUBE' or self.type == 'TORUS':
        return
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)

    bm.edges.ensure_lookup_table()
    for edge in bm.edges:
        e_angle = math.degrees(edge.calc_face_angle())

        if e_angle < self.angle:
            #print(e_angle)
            edge.select = False
            #print(edge.select)

    bmesh.update_edit_mesh(me)
    bm.free()  # free and prevent further access

    bpy.ops.transform.edge_crease(value=self.crease)
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = self.subdivision
    bpy.ops.object.convert(target='MESH')

