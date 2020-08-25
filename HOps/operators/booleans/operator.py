import bpy
import bmesh
from ... utils.objects import set_active
from ... material import assign_material
from ... preferences import get_preferences
from ... utility import collections, modifier
from ... utility.renderer import cycles
from . editmode_knife import edit_bool_knife

# TODO: Add KNIFE

def add(context, operation='DIFFERENCE', collection='Cutters', boolshape=True, sort=True, outset=False, thickness=0.5, keep_bevels=False, parent=False):

    selection = context.selected_objects
    active_object = context.active_object
    cutters = [object for object in selection if object != active_object and object.type in { "MESH", 'FONT', 'CURVE', 'SURFACE'}]


    cutters = [swap_cutter(context, o) if o.type!='MESH' else o  for o in cutters ]

    if get_preferences().property.workflow == "NONDESTRUCTIVE":
        for cutter in cutters:
            if active_object.data.use_auto_smooth:
                cutter.data.use_auto_smooth = True
                for f in cutter.data.polygons:
                    f.use_smooth = True

    for cutter in cutters:
        if cutter.rigid_body:
            set_active(cutter)
            bpy.ops.rigidbody.object_remove()

        if boolshape:
            cutter.display_type = 'WIRE'
            cutter.hops.status = "BOOLSHAPE"
            cutter.hide_render = True
            cycles.hide_preview(context, cutter)

            collections.unlink_obj(context, cutter)
            collections.link_obj(context, cutter, collection)

        if parent:
            if cutter.parent != active_object:
                temp_matrix = cutter.matrix_world
                cutter.parent = active_object
                cutter.matrix_world = temp_matrix
                #cutter.matrix_parent_inverse = active_object.matrix_world.inverted()

        data = cutter.data
        data.use_customdata_edge_bevel = True

        if operation in {'SLASH', 'INSET'}:
            # TODO: material setup to be moved away
            index = 0
            option = context.window_manager.Hard_Ops_material_options
            if option.active_material:
                mats = [slot.material for slot in active_object.material_slots if slot.material]
                if bpy.data.materials[option.active_material] not in mats:
                    mats.append(bpy.data.materials[option.active_material])
                    bpy.ops.object.material_slot_add()
                    active_object.material_slots[-1].material = bpy.data.materials[option.active_material]
                index = mats.index(bpy.data.materials[option.active_material])

            new_obj = active_object.copy()
            new_obj.data = active_object.data.copy()

            for col in active_object.users_collection:
                if col not in new_obj.users_collection:
                    col.objects.link(new_obj)

            if operation == 'INSET':
                new_obj.display_type = 'WIRE'
                new_obj.hops.status = "BOOLSHAPE"
                new_obj.hide_render = True
                cycles.hide_preview(context, new_obj)

                collections.unlink_obj(context, new_obj)
                collections.link_obj(context, new_obj, collection)

                if parent:
                    if cutter.parent != active_object:
                        new_obj.parent = active_object
                        new_obj.matrix_parent_inverse = active_object.matrix_world.inverted()

                for mod in new_obj.modifiers:
                    if mod.type == 'BEVEL' and not keep_bevels:
                        if mod.limit_method not in {'VGROUP', 'WEIGHT'}:
                            mod.show_render = mod.show_viewport = False
                    elif mod.type == 'WEIGHTED_NORMAL':
                        new_obj.modifiers.remove(mod)

                solidify = new_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
                solidify.show_expanded = True
                solidify.use_even_offset = True
                solidify.thickness = thickness
                solidify.offset = 0.0
                solidify.material_offset = index

            modifier_new_obj = new_obj.modifiers.new(name="Boolean", type="BOOLEAN")
            modifier_new_obj.operation = "INTERSECT"
            modifier_new_obj.object = cutter

            if operation == 'SLASH':
                if get_preferences().property.workflow == "DESTRUCTIVE":
                    set_active(new_obj)
                    modifier.apply(new_obj, type="BOOLEAN")

                assign_material(context, new_obj)

                new_obj.select_set(False)

        if operation in {'DIFFERENCE', 'UNION', 'INTERSECT', 'SLASH', 'INSET'}:
            boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
            if operation in {'SLASH', 'INSET'}:

                boolean.operation = 'DIFFERENCE'

                if operation == 'INSET':
                    if outset:
                        boolean.operation = 'UNION'
                    boolean.object = new_obj
                else:
                    boolean.object = cutter

            else:
                boolean.operation = operation
                boolean.object = cutter
                assign_material(context, cutter)

            boolean.show_expanded = False

        if sort:
            if operation == 'SLASH':
                modifier.user_sort(new_obj)

    if sort:
        modifier.user_sort(active_object)

    if operation == 'SLASH':
        modifier.sort(new_obj, sort_types=['WEIGHTED_NORMAL'])
    modifier.sort(active_object, sort_types=['WEIGHTED_NORMAL'])

    if get_preferences().property.workflow == "DESTRUCTIVE":
        if operation == 'INSET':
            set_active(new_obj, select=True, only_select=True)
        else:
            set_active(active_object, select=True, only_select=True)
            modifier.apply(active_object, type="BOOLEAN")
            for cutter in cutters:
                bpy.data.objects.remove(cutter, do_unlink=True)

    elif get_preferences().property.workflow == "NONDESTRUCTIVE":
        to_select = new_obj if operation == 'INSET' else cutters[0]
        set_active(to_select, select=True, only_select=True)


# TODO: Fix slash to others cut
# TODO: Fix Inset
def shift(context, operation='DIFFERENCE', collection='Cutters', boolshape=True, sort=True, outset=False, thickness=0.5, keep_bevels=False, parent=False):
    selection = context.selected_objects
    objects = [(obj, mod, mod.object) for obj in context.blend_data.objects if obj.users_collection for mod in obj.modifiers if mod.type == 'BOOLEAN' and mod.object if obj.hops.status == 'BOOLSHAPE' or obj.visible_get()]

    # doubles = [obj for obj in selection for mod in obj.modifiers if mod.type in ['BOOLEAN'] and mod.operation == 'INTERSECT' or mod.type in ['SOLIDIFY']]
    # slash = list(set(doubles))

    for obj, mod, cutter in objects:
        if cutter in selection:
            obj.modifiers.remove(mod)

    for obj in selection:
        obj.select_set(False)

    for obj, mod, cutter in objects:
        if cutter in selection:
            cutter.select_set(True)
            set_active(obj, select=True, only_select=False)
            add(context, operation=operation, collection=collection, boolshape=boolshape, sort=sort, outset=outset, thickness=thickness, keep_bevels=keep_bevels, parent=parent)
            cutter.select_set(False)
            obj.select_set(False)

    for obj in selection:
        obj.select_set(True)


# TODO: redo intersection with bmesh
# TODO: add material cutting
def knife(context, knife_project):
    selected = [o for o in context.selected_objects if o.type in {'MESH', 'CURVE'}]
    cutters = [o for o in selected if o is not context.active_object]
    if not cutters:
        return {'CANCELLED'}

    if knife_project:
        for cutter in cutters:
            edge_split = cutter.modifiers.new("Edge Split", 'EDGE_SPLIT')
            edge_split.use_edge_angle = True
            edge_split.split_angle = 0.0

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.knife_project(cut_through=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        for cutter in cutters:
            edge_split = cutter.modifiers[-1]
            cutter.modifiers.remove(edge_split)

    else:
        target = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(target.data)

        for cutter in cutters:
            target_geom = bm.verts[:] + bm.edges[:] + bm.faces[:]

            for mod in cutter.modifiers:
                mod.show_in_editmode = True

            depsgraph = context.evaluated_depsgraph_get()
            cutter = cutter.evaluated_get(depsgraph)
            mesh = cutter.to_mesh()

            mesh.transform(cutter.matrix_world)
            mesh.transform(target.matrix_world.inverted_safe())

            bm.from_mesh(mesh)
            cutter.to_mesh_clear()

            for g in bm.verts[:] + bm.edges[:] + bm.faces[:]:
                g.hide = False
                g.select = g not in target_geom

            edit_bool_knife(context, False, False)

        bpy.ops.object.mode_set(mode='OBJECT')

    if get_preferences().property.workflow == 'DESTRUCTIVE':
        for cutter in cutters:
            bpy.data.objects.remove(cutter, do_unlink=True)

    elif get_preferences().property.workflow == 'NONDESTRUCTIVE':
        context.active_object.select_set(False) # Can't change active object due to edit mode switch unfortunately

        for cutter in cutters:
            cutter.hops.status = 'BOOLSHAPE'
            cutter.display_type = 'WIRE'
            cutter.hide_render = True
            cycles.hide_preview(context, cutter)
            collections.unlink_obj(context, cutter)
            collections.link_obj(context, cutter, "Cutters")

    return {'FINISHED'}

def to_mesh (obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj, preserve_all_data_layers=False, depsgraph = depsgraph)

    return mesh

def swap_cutter(context, obj):

    cutter_mesh = to_mesh(obj)
    cutter_mesh.name = obj.data.name+"_mesh"
    cutter_obj = bpy.data.objects.new(obj.name+"_mesh", cutter_mesh)
    col=collections.find_collection(context, obj)
    col.objects.link(cutter_obj)
    obj.select_set(False)
    cutter_obj.select_set(True)

    cutter_obj.matrix_world = obj.matrix_world

    decimate = cutter_obj.modifiers.new("Decimate",type='DECIMATE')
    decimate.decimate_type = 'DISSOLVE'

    return cutter_obj
