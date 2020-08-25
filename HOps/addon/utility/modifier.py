import bpy
import bmesh

from mathutils import Vector


sort_types = [
    'BEVEL',
    'ARRAY',
    'MIRROR',
    'SOLIDIFY',
    'WEIGHTED_NORMAL',
    'SIMPLE_DEFORM',
    'TRIANGULATE',
    'DECIMATE',
    'REMESH',
    'SUBSURF',
]

if bpy.app.version[1] >= 82:
    sort_types.append('WELD')


def sort(obj, option=None, ignore=[], sort_types=sort_types, last_types=[], first=False, index_sort=True, ignore_hidden=True):
    modifiers = []

    if option:
        if not option.sort_modifiers:
            return

    for type in sort_types:
        sort = getattr(option, F'sort_{type.lower()}') if option else True
        sort_last = getattr(option, F'sort_{type.lower()}_last') if option else type in last_types
        last = False

        if not sort:
            continue

        for mod in reversed(obj.modifiers):
            visible = (mod.show_viewport and mod.show_render) or not ignore_hidden
            if mod in ignore or not visible:
                continue

            if not last and sort_last and mod.type == type:
                last = True
                modifiers.insert(0, mod)
            elif not sort_last and mod.type == type:
                modifiers.insert(0, mod)

    if not modifiers:
        return

    if index_sort:
        modifiers = sorted(modifiers, key=lambda mod: obj.modifiers[:].index(mod))

    unsorted = []
    for mod in reversed(obj.modifiers):
        if mod not in modifiers:
            unsorted.insert(0, mod)

    modifiers = modifiers + unsorted if first else unsorted + modifiers
    modifiers = [stored(mod) for mod in modifiers]

    obj.modifiers.clear()

    for mod in modifiers:
        new(obj, mod=mod)

    del modifiers


def apply(obj, mod=None, visible=False, modifiers=[], ignore=[], types={}):
    apply = []
    keep = []

    if mod:
        apply.append(mod)

    else:
        for mod in obj.modifiers:
            if (not modifiers or mod in modifiers) and mod not in ignore and (not visible or mod.show_viewport) and (not types or mod.type in types):
                apply.append(mod)

    for mod in obj.modifiers:
        if mod not in apply:
            keep.append(mod)

    keep = [stored(mod) for mod in keep]
    apply = [stored(mod) for mod in apply]

    if not apply:
        del keep

        return

    obj.modifiers.clear()

    for mod in apply:
        new(obj, mod=mod)

    if obj.data.users > 1:
        obj.data = obj.data.copy()

    ob = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    obj.data = bpy.data.meshes.new_from_object(ob)

    obj.modifiers.clear()

    for mod in keep:
        new(obj, mod=mod)

    del apply
    del keep


def bevels(obj, angle=False, weight=False, vertex_group=False, props={}):
    all = True
    bevel_mods = [mod for mod in obj.modifiers if mod.type == 'BEVEL']
    modifiers = []
    checked = lambda mod, method: mod not in modifiers and mod.limit_method == method

    if angle:
        all = False
        for mod in bevel_mods:
            if checked(mod, 'ANGLE'):
                modifiers.append(mod)
    if weight:
        all = False
        for mod in bevel_mods:
            if checked(mod, 'WEIGHT'):
                modifiers.append(mod)

    if vertex_group:
        all = False
        for mod in bevel_mods:
            if checked(mod, 'VGROUP'):
                modifiers.append(mod)

    if props:
        all = False

        for mod in bevel_mods:
            if mod in modifiers:
                continue

            for pointer in props:
                prop = hasattr(mod, pointer) and getattr(mod, pointer) == props[pointer]
                if not prop:
                    continue

                modifiers.append(mod)

    if all:
        return bevel_mods

    return sorted(modifiers, key=lambda mod: bevel_mods.index(mod))


def unmodified_bounds(self, obj, exclude={}):
    disabled = []
    for mod in obj.modifiers:
        if exclude and mod.type not in exclude and mod.show_viewport:
            disabled.append(mod)
            mod.show_viewport = False

    bpy.context.view_layer.update()

    bounds = [Vector(point[:]) for point in obj.bound_box[:]]

    for mod in disabled:
        mod.show_viewport = True

    del disabled

    return bounds


def stored(mod):
    exclude = {'__doc__', '__module__', '__slots__', 'bl_rna', 'rna_type', 'face_count'}
    namespace = type(mod.name, (), {})
    for pointer in dir(mod):
        if pointer not in exclude:

            type_string = str(type(getattr(mod, pointer))).split("'")[1]

            if type_string not in {'bpy_prop_array', 'Vector'}:
                setattr(namespace, pointer, getattr(mod, pointer))
            else:
                setattr(namespace, pointer, list(getattr(mod, pointer)))

    return namespace


def new(obj, name=str(), _type='BEVEL', mod=None, props={}):
    if mod:
        new = obj.modifiers.new(name=mod.name, type=mod.type)

        for pointer in dir(mod):
            if '__' in pointer or pointer in {'bl_rna', 'rna_type', 'type', 'custom_profile', 'face_count', 'falloff_curve', 'vertex_indices', 'vertex_indices_set'}:
                continue

            else:
                setattr(new, pointer, getattr(mod, pointer))

    elif _type:
        new = obj.modifiers.new(name=name, type=_type)

        if props:
            for pointer in props:
                if hasattr(new, pointer):
                    setattr(new, pointer, props[pointer])

        return new
