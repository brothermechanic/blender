import bpy


def apply_modifiers(object, modtype):
    for obj in object:
        if obj.type == "MESH":
            for mod in obj.modifiers:
                if mod.type in modtype:
                    bpy.ops.object.modifier_apply(apply_as="DATA", modifier=mod.name)


def remove_modifiers(object, modtype):
    # objects = bpy.data.objects
    for obj in object:
        if obj.type == "MESH":
            modifiers = obj.modifiers
            for mod in modifiers:
                if mod.type == modtype:
                    obj.modifiers.remove(mod)
