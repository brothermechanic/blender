import bpy
import gpu
from bgl import *
from math import radians, degrees
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import get_preferences
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from . import infobar
from ... utility.base_modal_controls import Base_Modal_Controls


class HOPS_OT_ModifierScroll(Operator):
    bl_idname = "hops.modifier_scroll"
    bl_label = "Scroll Modifiers"
    bl_description = "Use the scroll wheel to scroll through modifiers on the selected object"

    running: bool = False

    all: BoolProperty()
    type: StringProperty(default='BOOLEAN')
    additive : BoolProperty()


    def __init__(self):

        # Modal UI
        self.master = None


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        if event.shift:
            self.all = True

        if not self.all:
            self.modifiers = [mod for mod in context.active_object.modifiers if mod.type == self.type]

        else:
            self.modifiers = [mod for mod in context.active_object.modifiers]

        self.mods = {None: None}
        self.index = 0
        self.all_mods = False
        self.loop = False
        self.original_obj = context.active_object

        for mod in self.modifiers:
            if self.type == 'BOOLEAN' and not self.all and mod.show_render:
                self.mods.update({
                    mod: {
                        "original_show_viewport": mod.show_viewport,
                        "override": False,
                        "hide": mod.object.hide_viewport}})
            elif mod.show_render:
                self.mods.update({
                    mod: {
                        "original_show_viewport": mod.show_viewport,
                        "override": False,
                        "hide": False}})

        if len(self.mods) == 1:
            return {'CANCELLED'}

        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        modtoggle = False
        current_bool = None

        if self.base_controls.scroll:
            if event.shift:
                if self.mods[list(self.mods.keys())[self.index]] is not None:
                    mod = list(self.mods.keys())[self.index]
                    if self.base_controls.scroll ==1:
                        bpy.ops.object.modifier_move_up(modifier=mod.name)
                    else:
                        bpy.ops.object.modifier_move_down(modifier=mod.name)

            else:
                self.index += self.base_controls.scroll



        if self.loop:
            if self.index >= len(self.mods):
                self.index = 0
            if self.index < 0:
                self.index = len(self.mods) - 1

        else:
            self.index = max(min(self.index, len(self.mods) - 1), 0)

        if event.type == 'Z' and event.value == 'PRESS':
            context.object.show_wire = False if context.object.show_wire else True
            context.object.show_all_edges = True if context.object.show_wire else False
            self.report({'INFO'}, F'Show Wire : {context.object.show_all_edges}')

        if event.type == 'L' and event.value == 'PRESS':
            self.loop = not self.loop

        if event.type == 'A' and event.value == 'RELEASE':
            if self.mods[list(self.mods.keys())[self.index]] is not None:
                override_value = self.mods[list(self.mods.keys())[self.index]]["override"]
                self.mods[list(self.mods.keys())[self.index]]["override"] = not override_value

        self.original_obj.select_set(True)
        context.view_layer.objects.active = self.original_obj

        if event.type == "W" and event.value == "PRESS" and event.shift and self.mods[list(self.mods.keys())[self.index]] is not None:
            mod = list(self.mods.keys())[self.index]
            mod.show_render = not mod.show_render
            self.report({'INFO'}, F'Modifiers Renderability : {mod.show_render}')

        if event.type == "W" and event.value == "PRESS" and event.ctrl and not event.shift and self.mods[list(self.mods.keys())[self.index]] is not None:
            mod = list(self.mods.keys())[self.index]
            mod.show_render = not mod.show_render
            modtoggle = mod.show_render
            for mod in context.object.modifiers:
                mod.show_render = modtoggle
            modtoggle = not modtoggle
            self.report({'INFO'}, F'Modifier Renderability Re-enabled : {len(self.modifiers)}')

        # if event.type == "W" and event.value == "PRESS" and event.alt and not event.shift and not event.ctrl and self.mods[list(self.mods.keys())[self.index]] is not None:
        #     mod = list(self.mods.keys())[self.index]
        #     mod.show_viewport = not mod.show_viewport
        #     modtoggle = mod.show_viewport
        #     for mod in context.object.modifiers:
        #         mod.show_viewport = modtoggle
        #     modtoggle = not modtoggle
        #     self.report({'INFO'}, F'Modifier Visibility Re-enabled : {len(self.modifiers)}')

        if event.type == 'M' and event.value == 'PRESS' and event.shift == True:

            self.all_mods = not self.all_mods
            self.mods = {None: None}
            self.index = 0

            for mod in self.mods:
                if mod is not None:
                    mod.show_viewport = self.mods[mod]["original_show_viewport"]

            for mod in context.object.modifiers:
                if self.all_mods:
                    self.mods.update({mod: {"original_show_viewport": mod.show_viewport, "override": False}})

        if self.additive or event.shift:
            for count, mod in enumerate(self.mods):
                if mod is not None:
                    if count <= self.index:
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False
                    if self.mods[mod]["override"] or self.mods[list(self.mods.keys())[self.index]] is None:
                        mod.show_viewport = False

        else:
            for mod in self.mods:
                if mod and hasattr(mod, "object") and mod.object:
                    mod.show_viewport = self.mods[mod]["override"]  # hide all mods except for those pressed A on.
                    if not self.all or self.type == 'BOOLEAN':
                        mod.object.select_set(False)

                        mod.object.hide_viewport = True

                    if mod.show_viewport:  # show and select objects that have modifier being shown in viewport.
                        mod.object.hide_viewport = False

                        if not self.all or self.type == 'BOOLEAN':
                            mod.object.select_set(True)

            if self.mods[list(self.mods.keys())[self.index]] is not None:
                current_bool = list(self.mods.keys())[self.index]
                current_bool.show_viewport = True  # show viewport on the current mod.
                if hasattr(current_bool, "object"):

                    current_bool.object.hide_viewport = False

                    current_bool.object.select_set(True)

        if self.base_controls.confirm or event.type in { 'RET', 'NUMPAD_ENTER'}:

            for mod in self.mods:
                if mod is not None and hasattr(mod, "object"):
                    if not mod.show_viewport:
                        if not self.all or self.type == 'BOOLEAN' and mod.object:
                            mod.object.hide_viewport = True

                    elif not self.all or self.type == 'BOOLEAN' and mod.object:
                        mod.object.hide_viewport = False
                        mod.object.select_set(True)

            if not self.additive:
                if hasattr(current_bool, "object") and current_bool.object is not None:
                    context.active_object.select_set(False)
                    current_bool.object.select_set(True)
                    context.view_layer.objects.active = current_bool.object

            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        if self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        if self.base_controls.cancel or event.type in { 'BACK_SPACE'}:

            for mod in self.mods:
                if mod is not None:
                    mod.show_viewport = self.mods[mod]["original_show_viewport"]

            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        self.draw_master(context=context)

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


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
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                #win_list.append("Modifier Scroll")

                if self.index == 0:
                    win_list.append("Unmodified Mesh")

                else:
                    win_list.append(str(self.index))

                if list(self.mods.keys())[self.index] is not None:
                    mod = list(self.mods.keys())[self.index]

                    # Mod name
                    active_mod = mod.name

                    win_list.append("{}".format(mod.name))
                    #if hasattr(mod, "object") and mod.object:
                    #    win_list.append("{}".format(mod.object.name))

                else:
                    win_list.append("Modifiers Disabled")
            else:
                win_list.append("Modifier Scroll")

                if self.index == 0:
                    win_list.append("Unmodified Mesh")

                else:
                    win_list.append(str(self.index))

                if list(self.mods.keys())[self.index] is not None:
                    mod = list(self.mods.keys())[self.index]

                    # Mod name
                    active_mod = mod.name

                    win_list.append("{}".format(mod.name))
                    if hasattr(mod, "object") and mod.object:
                        win_list.append("{}".format(mod.object.name))

                    win_list.append("Render Visibility :" + str(mod.show_render))

                else:
                    win_list.append("Modifiers Disabled")

            # Help
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["Ctrl + W",  "(all) Toggle Renderability / Sort Lock"])
            help_list.append(["Scroll",    "Change boolean visibility"])
            help_list.append(["A",         "Toggle current visibility"])
            help_list.append(["M ",        "Use only booleans / all modifiers"])
            help_list.append(["L",         "Toggle looping"])
            help_list.append(["Z",         "Wire display"])
            help_list.append(["W",         "Toggle Renderability / Sort Lock"])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["~",         "Toggle viewport displays."])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(
                win_list=win_list,
                help_list=help_list,
                image="LateParent",
                mods_list=mods_list,
                active_mod_name=active_mod)

        # Finished
        self.master.finished()
