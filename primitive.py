import bpy
import bmesh
from math import sin, cos, pi
from mathutils import Vector


def create_capsule(self, name="Capsule"):
    # La metà del cilindro, esclusi i due emisferi
    half_cyl_height = (self.height - 2 * self.radius) / 2
    verts = []
    faces = []

    # === Calotta superiore: dall'alto (theta=pi/2) verso equatore (theta=0)
    for i in range(self.rings + 1):
        theta = (pi / 2) * (1 - i / self.rings)
        z = self.radius * sin(theta) + half_cyl_height
        r = self.radius * cos(theta)
        for j in range(self.segments):
            phi = 2 * pi * j / self.segments
            x = r * cos(phi)
            y = r * sin(phi)
            verts.append(Vector((x, y, z)))

    # === Cilindro
    for i in range(2):
        z = half_cyl_height - i * (2 * half_cyl_height)
        for j in range(self.segments):
            phi = 2 * pi * j / self.segments
            x = self.radius * cos(phi)
            y = self.radius * sin(phi)
            verts.append(Vector((x, y, z)))

    # === Calotta inferiore: dall'equatore (theta=0) verso il basso (theta=-pi/2)
    for i in range(1, self.rings + 1):
        theta = (pi / 2) * (i / self.rings)
        z = -self.radius * sin(theta) - half_cyl_height
        r = self.radius * cos(theta)
        for j in range(self.segments):
            phi = 2 * pi * j / self.segments
            x = r * cos(phi)
            y = r * sin(phi)
            verts.append(Vector((x, y, z)))

    # === Polo inferiore (ultimo vertice)
    verts.append(Vector((0, 0, -self.radius - half_cyl_height)))
    south_pole_index = len(verts) - 1

    # === Connessione facce tra layer
    def ring_face(start1, start2):
        for i in range(self.segments):
            next_i = (i + 1) % self.segments
            a = start1 + i
            b = start1 + next_i
            c = start2 + next_i
            d = start2 + i
            faces.append([a, b, c, d])

    layers = (self.rings + 1) + 2 + (self.rings)  # totale di "ring" generati
    for i in range(layers - 1):
        start1 = i * self.segments
        start2 = (i + 1) * self.segments
        ring_face(start1, start2)

    # === Triangoli finali sul polo sud
    last_ring_start = (layers - 1) * self.segments
    for i in range(self.segments):
        next_i = (i + 1) % self.segments
        faces.append([
            last_ring_start + i,
            last_ring_start + next_i,
            south_pole_index
        ])

    # === Mesh creation
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = self.subdivision
    bpy.ops.object.convert(target='MESH')
    return obj

import bpy
import bmesh
from math import sin, cos, pi
from mathutils import Vector

def create_soft_cone(self,name="SoftCone"):
    verts = []
    faces = []

    # === Apice del cono (punta)
    top = Vector((0, 0, self.height))
    verts.append(top)
    top_index = 0

    # === Corpo laterale del cono: da punta a base
    for i in range(1, self.rings + 1):
        t = i / self.rings
        r = t * self.radius
        z = self.height * (1 - t)
        for j in range(self.segments):
            phi = 2 * pi * j / self.segments
            x = r * cos(phi)
            y = r * sin(phi)
            verts.append(Vector((x, y, z)))

    # === Base piatta: cerchi concentrici da esterno verso interno (semisfera schiacciata)
    for i in range(self.rings, -1, -1):  # inverso per scendere
        r = self.radius * (i / self.rings)
        z = 0
        for j in range(self.segments):
            phi = 2 * pi * j / self.segments
            x = r * cos(phi)
            y = r * sin(phi)
            verts.append(Vector((x, y, z)))

    # === Centro della base
    base_center_index = len(verts)
    verts.append(Vector((0, 0, 0)))

    # === Connessione facce (dalla punta in basso)
    for i in range(self.rings):
        ring_start = 1 + (i - 1) * self.segments if i > 0 else top_index
        curr_ring = 1 + i * self.segments
        for j in range(self.segments):
            next_j = (j + 1) % self.segments
            if i == 0:
                # Triangoli dalla punta al primo anello
                faces.append([top_index, curr_ring + next_j, curr_ring + j])
            else:
                # Quad strip tra anelli
                a = ring_start + j
                b = ring_start + next_j
                c = curr_ring + next_j
                d = curr_ring + j
                faces.append([a, b, c, d])

    # === Base: connessioni tra cerchi concentrici
    base_start = 1 + self.rings * self.segments
    for i in range(self.rings - 1):
        ring1 = base_start + i * self.segments
        ring2 = base_start + (i + 1) * self.segments
        for j in range(self.segments):
            next_j = (j + 1) % self.segments
            a = ring1 + j
            b = ring1 + next_j
            c = ring2 + next_j
            d = ring2 + j
            faces.append([a, b, c, d])

    # === Triangoli verso il centro della base
    last_ring = base_start + (self.rings - 1) * self.segments
    for j in range(self.segments):
        next_j = (j + 1) % self.segments
        a = last_ring + j
        b = last_ring + next_j
        faces.append([a, b, base_center_index])

    # === Mesh finale
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = self.subdivision
    bpy.ops.object.convert(target='MESH')
    return obj




