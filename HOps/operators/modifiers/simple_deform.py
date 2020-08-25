import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import get_preferences
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list


class HOPS_OT_MOD_Simple_deform(bpy.types.Operator):
    bl_idname = "hops.mod_simple_deform"
    bl_label = "Adjust Simple Deform Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """
LMB - Adjust Deform Modifier
LMB + Ctrl - Add new Deform Modifier
LMB + Ctrl + Shift - Apply Deform Modifiers

Press H for help."""

    deform_objects = {}

    def __init__(self):

        # Modal UI
        self.master = None

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def deform_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SIMPLE_DEFORM"]

    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context=context, event=event)
        self.fisnish = False
        self.deform_objects = {}

        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            self.get_deform_modifier(object, event)

        if self.fisnish:
            return {'FINISHED'}

        self.active_deform_modifier = context.object.modifiers[self.deform_objects[context.object.name]["modifier"]]
        self.store_values()

        self.snap_buffer = 0
        self.snap_break = 0.1
        # UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context=context, event=event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        context.area.header_text_set("Hardops Simple Deform:        X/Y/Z : axis - {}      ctrl+X : Lock x - {}       ctrl+Y : Lock y: {}      ctrl+Z : Lock Z: {}".format(self.active_deform_modifier.deform_axis, self.active_deform_modifier.lock_x, self.active_deform_modifier.lock_y, self.active_deform_modifier.lock_z))

        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]

            if event.ctrl:

                self.snap_buffer += self.base_controls.mouse

                if abs(self.snap_buffer) > self.snap_break:
                    increment = math.radians(15)
                    modifier.angle = snap(modifier.angle, increment) + math.copysign(increment, self.snap_buffer)
                    self.snap_buffer = 0
            else:
                modifier.angle += self.base_controls.mouse

            if self.base_controls.scroll:
                if event.shift:
                    if self.base_controls.scroll == 1:
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=modifier.name)
                else:
                    deform_method_types = ["TWIST", "BEND", "TAPER", "STRETCH"]
                    modifier.deform_method = deform_method_types[(deform_method_types.index(modifier.deform_method) + self.base_controls.scroll) % len(deform_method_types)]

            if event.type == "X" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_x = not modifier.lock_x
                else:
                    modifier.deform_axis = "X"
            if event.type == "Y" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_y = not modifier.lock_y
                else:
                    modifier.deform_axis = "Y"
            if event.type == "Z" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_z = not modifier.lock_z
                else:
                    modifier.deform_axis = "Z"

            if self.base_controls.tilde and event.shift == True:
                bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

            if self.base_controls.cancel:
                self.restore()
                context.area.header_text_set(text=None)
                context.window_manager.event_timer_remove(self.timer)
                self.master.run_fade()
                return {'CANCELLED'}

            if self.base_controls.confirm:
                context.area.header_text_set(text=None)
                context.window_manager.event_timer_remove(self.timer)
                self.master.run_fade()
                return {'FINISHED'}

            if event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

            if event.type == "W" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=modifier.name)

        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}

    def get_deform_modifier(self, object, event):
        if event.ctrl:
            if event.shift:
                modifier.apply(object, type="SIMPLE_DEFORM")
                self.fisnish = True
            else:
                self.add_deform_modifier(object)
        else:
            try: self.deform_objects.setdefault(object.name, {})["modifier"] = self.deform_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        deform_modifier = object.modifiers.new(name="SimpleDeform", type="SIMPLE_DEFORM")
        deform_modifier.angle = math.radians(45)
        deform_modifier.deform_method = "TWIST"
        deform_modifier.deform_axis = "X"
        deform_modifier.lock_x = False
        deform_modifier.lock_y = False
        deform_modifier.lock_z = False

        self.deform_objects.setdefault(object.name, {})["modifier"] = deform_modifier.name
        self.deform_objects[object.name]["added_modifier"] = True

    def store_values(self):
        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]
            self.deform_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.deform_objects[object_name]["angle"] = modifier.angle
            self.deform_objects[object_name]["deform_method"] = modifier.deform_method
            self.deform_objects[object_name]["deform_axis"] = modifier.deform_axis
            self.deform_objects[object_name]["lock_x"] = modifier.lock_x
            self.deform_objects[object_name]["lock_y"] = modifier.lock_y
            self.deform_objects[object_name]["lock_z"] = modifier.lock_z

    def restore(self):
        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.deform_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.deform_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]
                modifier.show_viewport = self.deform_objects[object_name]["show_viewport"]
                modifier.angle = self.deform_objects[object_name]["angle"]
                modifier.deform_method = self.deform_objects[object_name]["deform_method"]
                modifier.deform_axis = self.deform_objects[object_name]["deform_axis"]
                modifier.lock_x = self.deform_objects[object_name]["lock_x"]
                modifier.lock_y = self.deform_objects[object_name]["lock_y"]
                modifier.lock_z = self.deform_objects[object_name]["lock_z"]

    def draw_master(self, context):

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################

        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: # Fast Floating
                win_list.append("{}".format(self.active_deform_modifier.deform_axis))
                win_list.append("{:.3f}".format(math.degrees(self.active_deform_modifier.angle)))
                win_list.append("{}".format(self.active_deform_modifier.deform_method))
            else:
                win_list.append("Simple Deform")
                win_list.append("{}".format(self.active_deform_modifier.deform_axis))
                win_list.append("Angle: {:.3f}".format(math.degrees(self.active_deform_modifier.angle)))
                win_list.append("Method: {}".format(self.active_deform_modifier.deform_method))

            # Help
            help_list.append(["Scroll", "Set deform method"])
            help_list.append(["Ctrl",   "Snap to 5*"])
            help_list.append(["X",      "Set axis/ ctrl - lock axis"])
            help_list.append(["Y",      "Set axis/ ctrl - lock axis"])
            help_list.append(["Z",      "Set axis/ ctrl - lock axis"])
            help_list.append(["Q",          "Move mod DOWN"])
            help_list.append(["W",          "Move mod UP"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["M",      "Toggle mods list."])
            help_list.append(["H",      "Toggle help."])
            help_list.append(["~",      "Toggle viewport displays."])

            # Mods
            if self.active_deform_modifier != None:
                active_mod = self.active_deform_modifier.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="AdjustBevel", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()


def snap(value, increment):
        result = round(value / increment) * increment
        return result
