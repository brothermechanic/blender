import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import get_preferences
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from . import infobar
from ... utility.base_modal_controls import Base_Modal_Controls

class HOPS_OT_AdjustCurveOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_curve"
    bl_label = "Adjust Curve"
    bl_description = "Interactive Curve adjustment. 1/2/3 provides presets for curves"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    second_value: IntProperty()

    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "CURVE"


    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        self.depth_offset += self.base_controls.mouse
        self.curve.data.bevel_depth =  self.start_depth_offset + self.depth_offset

        if self.base_controls.scroll:
            #bevel res
            if event.ctrl :
                self.curve.data.resolution_u += self.base_controls.scroll
                self.curve.data.render_resolution_u += self.base_controls.scroll
                self.report({'INFO'}, F'Curve Resolution : {self.curve.data.resolution_u}')
            #curve order
            elif event.shift :
                for spline in self.curve.data.splines:
                        spline.order_u += self.base_controls.scroll
                self.report({'INFO'}, F'Spline order:{self.curve.data.splines[0].order_u }')
            #bevel res
            else:
                    self.curve.data.bevel_resolution += self.base_controls.scroll
                    self.report({'INFO'}, F'Curve Bevel Resolution : {self.curve.data.bevel_resolution}')

        if event.type == 'S' and event.value == 'PRESS':

            if not event.shift:
                for spline in self.curve.data.splines:
                    spline.use_smooth = not spline.use_smooth
                smooth = self.curve.data.splines[0].use_smooth
                shade ={True:"Smooth", False:"Flat"}
                self.report({'INFO'}, F'Shade {shade[smooth]}')
            else:
                for spline in self.curve.data.splines:
                    spline.use_smooth = self.curve.data.splines[0].use_smooth
                self.report({'INFO'}, F'Shading Synced')

        edgeSplit = [mod.name for mod in self.curve.modifiers if mod.type == 'EDGE_SPLIT']

        if event.type == 'C' and event.value == 'PRESS':
            for spline in self.curve.data.splines:
                length_limit = False
                if spline.type == 'BEZIER'and len(spline.bezier_points)>1 :
                    length_limit = True
                elif len(spline.points) >2:
                    length_limit = True
                spline.use_cyclic_u = not spline.use_cyclic_u if length_limit else False
            self.report({'INFO'}, F'Toggled Cyclic')

        if event.type == 'W' and event.value == 'PRESS':
            self.curve.show_wire = not self.curve.show_wire
            wire ={True:"ON", False:"OFF"}
            self.report({'INFO'}, F'Wireframe:{wire[self.curve.show_wire]}')

        if event.type == 'F' and event.value == 'PRESS':
            self.fill_index= self.fill_index+1 if self.fill_index<3 else 0
            self.curve.data.fill_mode = self.fill_type[self.fill_index]
            self.report({'INFO'}, F'Fill Mode:{self.curve.data.fill_mode}')

        if event.type == 'V' and event.value == 'PRESS':
            self.spline_type_index = self.spline_type_index+1 if self.spline_type_index<2 else 0
            self.curve.data.splines[0].type = self.spline_type[self.spline_type_index]
            if self.curve.data.splines[0].type != 'BEZIER' and self.spline_type_index == 2:
                self.spline_type_index =0
            for spline in self.curve.data.splines:
                    spline.type = self.spline_type[self.spline_type_index]
                    self.spline_type[self.spline_type_index]
                    spline.order_u = spline.order_u
            self.report({'INFO'}, F'Spline type:{self.curve.data.splines[0].type}')

        if event.type == 'ONE' and event.value == 'PRESS':
            self.curve.data.resolution_u = 6
            self.curve.data.render_resolution_u = 12
            self.curve.data.bevel_resolution = 6
            self.curve.data.fill_mode = 'FULL'
            self.report({'INFO'}, F'Resolution : 6')

            for name in edgeSplit:
                bpy.ops.object.modifier_remove(modifier=name)

        if event.type == 'TWO' and event.value == 'PRESS':
            self.curve.data.resolution_u = 64
            self.curve.data.render_resolution_u = 64
            self.curve.data.bevel_resolution = 16
            self.curve.data.fill_mode = 'FULL'
            self.report({'INFO'}, F'Resolution : 64')

            for name in edgeSplit:
                bpy.ops.object.modifier_remove(modifier=name)

        if event.type == 'THREE' and event.value == 'PRESS':
            self.curve.data.resolution_u = 64
            self.curve.data.render_resolution_u = 64
            self.curve.data.bevel_resolution = 0
            self.curve.data.fill_mode = 'FULL'
            if not len(edgeSplit):
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                self.curve.modifiers["EdgeSplit"].split_angle = math.radians(60)
            self.report({'INFO'}, F'Resolution : 64 / Edge Split Added')

        if self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        if self.base_controls.confirm:
            if not self.start_show_wire:
                self.curve.show_wire = False
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if event.type == 'X' and event.value == 'PRESS':
            self.curve.data.bevel_depth = 0.0
            self.report({'INFO'}, F'Depth Set To 0 - exit')
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if self.base_controls.cancel:
            self.reset_object()
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}



        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def reset_object(self):
        self.curve.data.bevel_depth = self.start_depth_offset
        self.curve.show_wire = self.start_show_wire
        self.curve.data.fill_mode = self.start_fill_mode
        self.curve.data.bevel_depth = self.start_bevel_depth
        for spline in self.curve.data.splines:
            spline.type = self.start_spline_type
            spline.order_u =self.start_order_u


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        self.curve = context.active_object
        self.master = None
        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.start_depth_offset = self.curve.data.bevel_depth
        self.depth_offset = 0
        self.profile_offset = 0
        # grab init parameters
        self.start_show_wire = self.curve.show_wire
        self.start_fill_mode = self.curve.data.fill_mode
        self.start_bevel_depth = self.curve.data.bevel_depth
        self.start_order_u = self.curve.data.splines[0].order_u
        self.fill_type =["FULL", "BACK", "FRONT", "HALF"]
        self.fill_index = self.fill_type.index(self.start_fill_mode)
        self.start_spline_type = self.curve.data.splines[0].type
        self.spline_type = ["POLY", "NURBS", "BEZIER"]
        self.spline_type_index = self.spline_type.index(self.start_spline_type)
        if self.curve:
            self.first_value = self.curve.data.bevel_depth

            #UI System
            self.master = Master(context=context)
            self.master.only_use_fast_ui = True

            context.window_manager.modal_handler_add(self)
            infobar.initiate(self)
            return {"RUNNING_MODAL"}

        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


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
                win_list.append("{:.2f}".format(self.curve.data.bevel_depth))
                win_list.append("{:.0f}".format(self.curve.data.render_resolution_u))
                win_list.append("{:.0f}".format(self.curve.data.bevel_resolution))
            else:
                win_list.append("Curve Adjust")
                win_list.append(self.curve.data.splines[0].type)
                win_list.append(F"Fill type: {self.curve.data.fill_mode}")
                win_list.append("Width - {:.3f}".format(self.curve.data.bevel_depth))
                win_list.append("Segments (ctrl) - {:.0f}".format(self.curve.data.render_resolution_u))
                win_list.append("Profile:{:.0f}".format(self.curve.data.bevel_resolution))
                win_list.append("Order:{:.0f}".format(self.curve.data.splines[0].order_u))
            # Help
            help_list.append(["X",             "Set Depth to 0 and end"])
            help_list.append(["C",             "Toggle cyclic"])
            help_list.append(["V",             "Cycle spline type"])
            help_list.append(["SHIFT+S",       "Sync spline shading"])
            help_list.append(["S",             "Toggle smooth shading"])
            help_list.append(["W",             "Toggle Wireframe"])
            help_list.append(["F",             "Cycle Fill Mode"])
            help_list.append(["3",             "Set profile 64 x 4 (Box)"])
            help_list.append(["2",             "Set profile 64 x 16"])
            help_list.append(["1",             "Set profile 12 x 6"])
            help_list.append(["Shift + Scroll", "Set  order"])
            help_list.append(["Ctrl + Scroll", "Set segments"])
            help_list.append(["Scroll",        "Set resolution"])
            help_list.append(["Mouse",          "Adjust Bevel Depth"])
            help_list.append(["M",             "Toggle mods list."])
            help_list.append(["H",             "Toggle help."])
            help_list.append(["~",             "Toggle viewport displays."])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Curve", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
