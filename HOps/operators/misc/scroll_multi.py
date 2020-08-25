import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

class HOPS_OT_ScrollMulti(bpy.types.Operator):
    bl_idname = "hops.scroll_multi"
    bl_label = "Bool / Modifier Management system"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Bool Scroll
LMB + SHIFT - Modifier Scroll
LMB + CTRL - Toggle Modifiers
LMB + ALT - Apply Modifiers

"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl and event.shift:
            #Toggle Modifiers
            bpy.ops.hops.bool_toggle_viewport('INVOKE_DEFAULT', all_modifiers=True)
            self.report({'INFO'}, F'Modifier Toggle')
        elif event.alt and event.ctrl:
            self.report({'INFO'}, F'Other Case Worked')
        elif event.shift:
            #Additive Scroll
            bpy.ops.hops.modifier_scroll('INVOKE_DEFAULT',all=True, additive=True)
            self.report({'INFO'}, F'Modifier Scroll')
            #bpy.ops.hops.modifier_scroll('INVOKE_DEFAULT', type="BOOLEAN", additive=True)
        elif event.ctrl:
            #Toggle Modifiers
            bpy.ops.hops.bool_toggle_viewport('INVOKE_DEFAULT', all_modifiers=True)
            self.report({'INFO'}, F'Modifier Toggle')
        elif event.alt:
            #Apply Modifiers
            #bpy.ops.hops.mod_apply()
            bpy.ops.object.convert(target='MESH')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            self.report({'INFO'}, F'Converted To Mesh')
        else:
            #Object Scroll
            bpy.ops.hops.bool_scroll_objects('INVOKE_DEFAULT')
            self.report({'INFO'}, F'Object Scroll')

        return {'FINISHED'}
