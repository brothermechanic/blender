import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list

class HOPS_OT_MOD_Weld(bpy.types.Operator):
    bl_idname = "hops.mod_weld"
    bl_label = "Adjust Weld Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Adjust Weld Modifier
LMB + CTRL - Add new Weld Modifier

Press H for help"""

    weld_objects = {}

    def __init__(self):

        # Modal UI
        self.master = None

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def weld_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "WELD"]

    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object else self.objects[0]

        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.weld_objects = {}

        self.snap_buffer = 0
        self.snap_break = 0.1

        for object in self.objects:
            self.get_weld_modifier(context, object, event)
            object.show_wire = True
            object.show_all_edges = True

        self.store_values()

        self.active_weld_modifier = context.object.modifiers[self.weld_objects[context.object.name]["modifier"]]

        for object in self.objects:
            modifier.sort(object, sort_types=['WEIGHTED_NORMAL'])

        # UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        offset = self.base_controls.mouse / 10
        if not event.ctrl:
            merge_threshold_offset = offset
        else:
            merge_threshold_offset = 0
        context.area.header_text_set("Hardops weld:     merge threshold: {:.4f}".format(self.active_weld_modifier.merge_threshold))

        for object_name in self.weld_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.weld_objects[object_name]["modifier"]]

            if event.ctrl:
                self.snap_buffer += self.base_controls.mouse
                if abs(self.snap_buffer) > self.snap_break:
                    modifier.max_interactions = snap(modifier.max_interactions, 1) + math.copysign(1, self.snap_buffer)
                    self.snap_buffer = 0

            else:
                modifier.merge_threshold = self.weld_objects[object_name]["buffer_threshold"] + merge_threshold_offset
                self.weld_objects[object_name]["buffer_threshold"] = modifier.merge_threshold

            if self.base_controls.tilde and event.shift == True:
                bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

            if self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll ==1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                else:
                    modifier.merge_threshold += 0.005 * self.base_controls.scroll
                    self.weld_objects[object_name]["buffer_threshold"] = modifier.merge_threshold

            if event.type == "Z" and event.value == "PRESS":
                object.show_wire = False if object.show_wire else True
                object.show_all_edges = True if object.show_wire else False
                # self.report({'INFO'}, F'Show Wire : {object.show_all_edges}')

            if self.base_controls.cancel:
                object.show_wire = False
                object.show_all_edges = False
                self.restore()
                context.area.header_text_set(text=None)
                context.window_manager.event_timer_remove(self.timer)
                self.master.run_fade()
                return {'CANCELLED'}

            if self.base_controls.confirm:
                object.show_wire = False
                object.show_all_edges = False
                context.area.header_text_set(text=None)
                context.window_manager.event_timer_remove(self.timer)
                self.master.run_fade()
                return {'FINISHED'}




        self.active_weld_modifier = self.object.modifiers[self.weld_objects[self.object.name]["modifier"]]
        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}

    def get_weld_modifier(self, context, object, event):
        if event.ctrl:
            mod = self.add_weld_modifier(context, object)
        else:
            try: self.weld_objects.setdefault(object.name, {})["modifier"] = self.weld_modifiers(object)[-1].name
            except: self.add_weld_modifier(context, object)

    def add_weld_modifier(self, context, object):

        weld_modifier = object.modifiers.new(name="Weld", type="WELD")
        weld_modifier.merge_threshold = 0.0001
        weld_modifier.max_interactions = 0

        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            weld_modifier.vertex_group = vg.name

        self.weld_objects.setdefault(object.name, {})["modifier"] = weld_modifier.name
        self.weld_objects[object.name]["added_modifier"] = True

    def store_values(self):
        for object_name in self.weld_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.weld_objects[object_name]["modifier"]]
            self.weld_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.weld_objects[object_name]["merge_threshold"] = modifier.merge_threshold
            self.weld_objects[object_name]["max_interactions"] = modifier.max_interactions
            self.weld_objects[object_name]["buffer_threshold"] = modifier.merge_threshold
            self.weld_objects[object_name]["buffer_interactions"] = modifier.max_interactions

    def restore(self):
        for object_name in self.weld_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.weld_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.weld_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.weld_objects[object_name]["modifier"]]
                modifier.show_viewport = self.weld_objects[object_name]["show_viewport"]
                modifier.merge_threshold = self.weld_objects[object_name]["merge_threshold"]
                modifier.max_interactions = self.weld_objects[object_name]["max_interactions"]
        self.original_viewport = bpy.context.space_data.overlay.show_overlays
        self.show_wireframes = bpy.context.space_data.overlay.show_wireframes

    def draw_master(self, context):

        # Start
        self.master.setup()

        #   Fast UI
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append("{:.4f}".format(self.active_weld_modifier.merge_threshold))
                win_list.append("{}".format(self.active_weld_modifier.max_interactions))
            else:
                win_list.append("Weld")
                win_list.append("Threshold: {:.4f}".format(self.active_weld_modifier.merge_threshold))
                win_list.append("Duplicate Limit: {}".format(self.active_weld_modifier.max_interactions))

            # Help
            help_list.append(["Move",       "Set merge threshold"])
            help_list.append(["Ctrl",       "Set interactions"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            #help_list.append(["Shift + Q",  "Space"])
            help_list.append(["Shift + Q",  "Move mod down"])
            help_list.append(["Shift + W",  "Move mod up"])
            help_list.append(["Z",          "Toggle wire display"])
            help_list.append(["H",          "Toggle help"])
            help_list.append(["M",          "Toggle mods list"])
            help_list.append(["~",          "Toggle viewport displays"])

            # Mods
            if self.active_weld_modifier != None:
                active_mod = self.active_weld_modifier.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="BevelMultiply", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()


def snap(value, increment):
        result = round(value / increment) * increment
        return result