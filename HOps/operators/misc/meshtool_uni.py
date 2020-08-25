import bpy
import bmesh
import bpy.utils.previews
from math import radians
from ... preferences import get_preferences
from ... utils.blender_ui import get_dpi_factor
from ... utils.context import ExecutionContext
from ... utility import modifier
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from ...ui_framework.operator_ui import Master


class HOPS_OT_ClearClean(bpy.types.Operator):
    bl_idname = "hops.clearclean"
    bl_label = "Cleans Mesh / Removes Sharpening"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = """LMB - Clean Mesh (CleanMesh)
LMB + CTRL - Remove Sharp Edges / Bevel Mod (clear-sharp)

"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl:
            self.report({'INFO'}, F'Sharp Markings Removed')
            bpy.ops.clean.sharps('INVOKE_DEFAULT')
        else:
            self.report({'INFO'}, F'Mesh Cleaned')
            bpy.ops.view3d.clean_mesh('INVOKE_DEFAULT')
        return {'FINISHED'}

class HOPS_OT_TwistApply(bpy.types.Operator):
    bl_idname = "hops.twist_apply"
    bl_label = "Twist 360 / Apply 360"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = """LMB - Twist 360
LMB + CTRL - Apply 360

"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl:
            self.report({'INFO'}, F'Radial 360 Applied')
            bpy.ops.clean.reorigin('INVOKE_DEFAULT', origin_set=True)
        else:
            self.report({'INFO'}, F'Twist 360')
            bpy.ops.array.twist('INVOKE_DEFAULT')
            #bpy.ops.array.twist()
        return {'FINISHED'}

class HOPS_OT_EditMultiTool(bpy.types.Operator):
    bl_idname = "hops.edit_multi_tool"
    bl_label = "Edit Multi-Tool"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_description = """LMB - Mark / Unmark Edge
LMB + CTRL - Add Bevel (vgroup)
LMB + SHIFT - Add Weld (vgroup)
LMB + ALT - Adjust Bevel Weight

"""
    called_ui = False

    header = "nothing"
    text = "nothing"

    def __init__(self):

        HOPS_OT_EditMultiTool.called_ui = False

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl:
            try:
                self.report({'INFO'}, F'Bevel Added')
                header = "Bevel"
                text = "Vgroup Bevel Added"
            except:
                header = "Failed"
                text = "Operation failed due to selection."
            bpy.ops.hops.adjust_bevel('INVOKE_DEFAULT')
        elif event.shift:
            header = "Weld Vgroup"
            text = "Vgroup Weld Added"
            bpy.ops.hops.mod_weld('INVOKE_DEFAULT')
            #bpy.ops.clean1.objects(clearsharps=False)
        elif event.alt:
            self.report({'INFO'}, F'Bevel Weight Adjustment')
            header = "Bevel Weight"
            text = "Bevel Weight Adjustment"
            bpy.ops.hops.bevel_weight('INVOKE_DEFAULT')
        else:
            header = "Mark"
            text = "Selection marked / unmarked"
            self.report({'INFO'}, F'Sharp Marked / Unmarked')
            bpy.ops.hops.set_edit_sharpen()

        # Operator UI
        if not HOPS_OT_EditMultiTool.called_ui:
            HOPS_OT_EditMultiTool.called_ui = True

            ui = Master()

            draw_data = [
                [header],
                [text]
            ]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}

class HOPS_OT_Bevel_Half_Add(bpy.types.Operator):
    bl_idname = "hops.bevel_half_add"
    bl_label = "Bevel Half"
    bl_options = {'REGISTER'}
    bl_description = """Add Bevel at half of last bevel.

    Cstep 3.0 ND

"""
    called_ui = False

    def __init__(self):

        HOPS_OT_Bevel_Half_Add.called_ui = False

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def execute(self, context):
        # Get Bevels
        obj = context.active_object
        bevel_widths = [mod.width for mod in obj.modifiers if mod.type == 'BEVEL']

        default = 0.2
        lw = bevel_widths[-1] if bevel_widths else default

        factor = 0.55
        lw = lw - lw * factor

        bevel_modifier = obj.modifiers.new(name="Bevel", type="BEVEL")
        bevel_modifier.width = lw

        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.segments = 6
        bevel_modifier.use_clamp_overlap = False
        bevel_modifier.harden_normals = False
        bevel_modifier.angle_limit = radians(60)
        bevel_modifier.loop_slide = get_preferences().property.bevel_loop_slide
        bevel_modifier.profile = get_preferences().property.bevel_profile

        modifier.sort(obj, sort_types=['WEIGHTED_NORMAL'])

        # Operator UI
        if not HOPS_OT_Bevel_Half_Add.called_ui:
            HOPS_OT_Bevel_Half_Add.called_ui = True

            ui = Master()
            draw_data = [
                ["Bevel Half"],
                ["Half Bevel Added", "60°"],
                ["Total Modifiers ", len(context.active_object.modifiers[:])]
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {'FINISHED'}

class HOPS_OT_BVL_MULTI(bpy.types.Operator):
    bl_idname = "hops.bevel_assist"
    bl_label = "Bevel Multi_Assist"
    bl_options = {'REGISTER'}
    bl_description = """LMB - Bevel Helper
CTRL - Bevel Divider
ALT - Bevel Multiply
LMB + SHIFT - Edge Manager

"""

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        if event.ctrl:
            self.report({'INFO'}, F'Bevel Divider')
            bpy.ops.view3d.bevel_multiplier('INVOKE_DEFAULT',multiply=False)
        elif event.shift:
            self.report({'INFO'}, F'Bevel Weight Adjustment')
            bpy.ops.hops.sharp_manager('INVOKE_DEFAULT')
            #bpy.ops.hops.bevel_weight()
        elif event.alt:
            self.report({'INFO'}, F'Bevel Multiplier')
            bpy.ops.view3d.bevel_multiplier('INVOKE_DEFAULT',multiply=True)
        else:
            try:
                bpy.ops.hops.bevel_helper('INVOKE_DEFAULT')
                self.report({'INFO'}, F'Bevel Helper')
            except:
                bpy.ops.hops.sharp_manager('INVOKE_DEFAULT')
                self.report({'INFO'}, F'No Bevels Present')
        return {'FINISHED'}

class HOPS_OT_BevBoolMulti(bpy.types.Operator):
    bl_idname = "hops.bev_multi"
    bl_label = "Bevel Boolean Multi_Assist"
    bl_options = {'REGISTER'}
    bl_description = """

"""

    def invoke(self, context, event):

        active_object = context.active_object
        is_bevel = len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'BEVEL'])
        is_bool = len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'BOOLEAN'])

        try:
            if len(bpy.context.selected_objects) == 1:
                if context.active_object.hops.status == 'BOOLSHAPE':
                    bpy.ops.hops.bool_shift('INVOKE_DEFAULT')
                elif is_bevel and context.active_object.hops.status != 'BOOLSHAPE':
                    bpy.ops.hops.bevel_helper('INVOKE_DEFAULT')
                    self.report({'INFO'}, F'Bevel Helper')
                elif is_bool:
                    bpy.ops.hops.bool_scroll_objects('INVOKE_DEFAULT')
                    self.report({'INFO'}, F'BoolScroll Fallback')
                else:
                    self.report({'INFO'}, F'Not Used')
                # elif object.mode == "EDIT":
                #     bpy.ops.hops.bool_modal('INVOKE_DEFAULT', operation='DIFFERENCE', ignore_sort=False)
            elif len(bpy.context.selected_objects) == 2:
                bpy.ops.hops.bool_modal('INVOKE_DEFAULT', operation='DIFFERENCE', ignore_sort=False)

            elif len(bpy.context.selected_objects) >= 3:
                bpy.ops.hops.bool_modal('INVOKE_DEFAULT', operation='SLASH', ignore_sort=False)

            else:
                self.report({'INFO'}, F'No Selection')
                return {'FINISHED'}

        except:
            self.report({'INFO'}, F'Nah')
            return {'FINISHED'}

        return {'FINISHED'}
