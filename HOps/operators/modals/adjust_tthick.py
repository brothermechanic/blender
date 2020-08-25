import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ... preferences import get_preferences
#from ... addon.utility import method_handler
from ... ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from . import infobar


class HOPS_OT_AdjustTthickOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_tthick"
    bl_label = "Adjust Tthick"
    bl_description = """LMB - Adjust SOLIDIFY modifier
LMB + Ctrl - Add New SOLIDIFY modifier

Press H for help"""
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}


    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    @staticmethod
    def solidify_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SOLIDIFY"]


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        self.objects = [o for o in context.selected_objects if o.type == 'MESH']
        self.object = context.active_object if context.active_object.type == 'MESH' else self.objects[0]

        for obj in self.objects:
            modifier.sort(obj, sort_types=['WEIGHTED_NORMAL'])


        self.solidify_mods = {}
        self.solidify = self.get_solidify_modifier(event)

        for obj in self.solidify_mods:
            self.solidify_mods[obj]["start_solidify_thickness"] = self.solidify_mods[obj]["solidify"].thickness
            self.solidify_mods[obj]["start_solidify_offset"] = self.solidify_mods[obj]["solidify"].offset

        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {"RUNNING_MODAL"}


    def get_solidify_modifier(self, event):
        for obj in self.objects:

            if obj not in self.solidify_mods:
                self.solidify_mods.update({obj: {"solidify": None, "start_solidify_thickness": 0, "start_solidify_offset": 0, "solidify_offset": 0, "thickness_offset": 0, "created_solidify_modifier": False}})
            mods = obj.modifiers

            if event.ctrl:
                solidify_modifier = obj.modifiers.new("Solidify", "SOLIDIFY")
                self.solidify_mods[obj]["solidify"] = solidify_modifier
                self.solidify_mods[obj]["created_solidify_modifier"] = True
                if get_preferences().property.force_thick_reset_solidify_init or self.solidify_mods[obj]["created_solidify_modifier"]:
                    solidify_modifier.thickness = 0
                    solidify_modifier.use_even_offset = True
                    solidify_modifier.use_quality_normals = True
                    solidify_modifier.use_rim_only = False
                    solidify_modifier.show_on_cage = True
            else:
                if "Solidify" in mods:
                    self.solidify_mods[obj]["solidify"] = obj.modifiers["Solidify"]
                    solidify_modifier = obj.modifiers["Solidify"]
                else:# if did not get one this iteration, create it
                    solidify_modifier = obj.modifiers.new("Solidify", "SOLIDIFY")
                    self.solidify_mods[obj]["solidify"] = solidify_modifier
                    self.solidify_mods[obj]["created_solidify_modifier"] = True
                if get_preferences().property.force_thick_reset_solidify_init or self.solidify_mods[obj]["created_solidify_modifier"]:
                    solidify_modifier.thickness = 0
                    solidify_modifier.use_even_offset = True
                    solidify_modifier.use_quality_normals = True
                    solidify_modifier.use_rim_only = False
                    solidify_modifier.show_on_cage = True


    def modal(self, context, event):

        # UI
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        offset_x = self.base_controls.mouse

        context.area.header_text_set("Hardops Adjust Thickness")

        for obj in self.solidify_mods:
            self.solidify = self.solidify_mods[obj]["solidify"]
            self.solidify_mods[obj]["thickness_offset"] += offset_x
            if event.ctrl:
                self.solidify.thickness = round(self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"], 1)
            else:
                self.solidify.thickness = self.solidify_mods[obj]["start_solidify_thickness"] + self.solidify_mods[obj]["thickness_offset"]

            if event.type == 'ONE' and event.value == 'PRESS':
                self.solidify.offset = -1
                self.solidify_mods[obj]["solidify_offset"] = 0
                self.report({'INFO'}, F'Solidify Offset : 0')

            if event.type == 'TWO' and event.value == 'PRESS':
                self.solidify.offset = 0
                self.solidify_mods[obj]["solidify_offset"] = -1
                self.report({'INFO'}, F'Solidify Offset : -1')

            if event.type == 'THREE' and event.value == 'PRESS':
                self.solidify.offset = 1
                self.solidify_mods[obj]["solidify_offset"] = -2
                self.report({'INFO'}, F'Solidify Offset : -2')

            if event.type == "Q" and event.value == "PRESS":
                bpy.ops.object.modifier_move_up(modifier=self.solidify.name)

            if event.type == "E" and event.value == "PRESS":
                bpy.ops.object.modifier_move_down(modifier=self.solidify.name)

            if self.base_controls.tilde and event.shift == True:
                 bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

            if event.type == 'R' and event.value == 'PRESS':
                self.solidify.use_rim_only = not self.solidify.use_rim_only
                self.report({'INFO'}, F'Rim Only : {self.solidify.use_rim_only}')

            if event.shift:
                if self.base_controls.scroll==1:
                    bpy.ops.object.modifier_move_up(modifier=self.solidify.name)
                if self.base_controls.scroll == -1:
                    bpy.ops.object.modifier_move_down(modifier=self.solidify.name)

            # solidify mode is 2.82 specific feature
            if (2, 82, 4)<bpy.app.version and event.type == 'FOUR' and event.value == 'PRESS':
                if self.solidify.solidify_mode == 'EXTRUDE':
                    self.solidify.solidify_mode = 'NON_MANIFOLD'
                else:
                    self.solidify.solidify_mode = 'EXTRUDE'
                self.report({'INFO'}, F'Mode : {self.solidify.solidify_mode}')

        if event.type == "H" and event.value == "PRESS":
            get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help

        if self.base_controls.cancel:
            self.reset_object()
            context.area.header_text_set(text=None)
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        if self.base_controls.confirm:
            context.area.header_text_set(text=None)
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}


        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def reset_object(self):

        for obj in self.solidify_mods:
            self.solidify = self.solidify_mods[obj]["solidify"]
            self.solidify.thickness = self.solidify_mods[obj]["start_solidify_thickness"]
            self.solidify.offset = self.solidify_mods[obj]["start_solidify_offset"]
            if self.solidify_mods[obj]["created_solidify_modifier"]:
                obj.modifiers.remove(self.solidify)

        self.solidify = None


    def finish(self, context):

        context.area.header_text_set(text=None)
        self.remove_ui()
        infobar.remove(self)
        return {"FINISHED"}


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
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                if self.solidify != None:
                    win_list.append("{:.2f}".format(self.solidify.thickness))
                    win_list.append("{}".format(self.solidify.use_rim_only))
                    win_list.append("{:.2f}".format(self.solidify.offset))
                else:
                    win_list.append("0")
                    win_list.append("Rim: Removed")
                    win_list.append("Offset: Removed")
            else:
                win_list.append("Solidify")
                if self.solidify != None:
                    win_list.append("{:.3f}".format(self.solidify.thickness))
                    win_list.append("Rim: {}".format(self.solidify.use_rim_only))
                    win_list.append("Offset: {:.2f}".format(self.solidify.offset))
                else:
                    win_list.append("0")
                    win_list.append("Rim: Removed")
                    win_list.append("Offset: Removed")


            # Help
            help_list.append(["R",                  "Turn rim on/off"])
            help_list.append(["Ctrl",               "Set thickness (snap)"])
            help_list.append(["Shift + Scroll",     "Move mod up/down"])
            help_list.append(["1",                  "Set offset to -1"])
            help_list.append(["2",                  "Set offset to 0"])
            help_list.append(["3",                  "Set offset to 1"])
            if self.solidify != None:
                help_list.append(["4",             F"Solidify Mode: {self.solidify.solidify_mode.capitalize()}"])
            help_list.append(["E / Q",              "Move mod up/down"])
            help_list.append(["M",                  "Toggle mods list"])
            help_list.append(["H",                  "Toggle help"])
            help_list.append(["~",                  "Toggle viewport displays"])

            # Mods
            if self.solidify != None:
                active_mod = self.solidify.name
            else:
                active_mod = ""

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
