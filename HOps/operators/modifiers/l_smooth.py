import bpy, bmesh, gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list

class HOPS_OT_MOD_LSmooth(bpy.types.Operator):
    bl_idname = "hops.mod_lsmooth"
    bl_label = "Adjust Smooth Modifier"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING', 'GRAB_CURSOR'}
    bl_description = """
LMB - Adjust Laplacian Smooth Modifier
LMB + Ctrl - Create new Smooth Modifier
LMB + Shift - Auto Vertex Group

Press H for help"""

    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        self.create_new = event.ctrl
        self.auto_vgroup = event.shift
        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.obj = context.active_object
        self.mods = [m for m in self.obj.modifiers if m.type == 'LAPLACIANSMOOTH']

        if not self.mods:
            self.create_new = True

        if self.create_new:
            self.mod = self.obj.modifiers.new("Laplacian Smooth", 'LAPLACIANSMOOTH')
            self.mods.append(self.mod)

        else:
            self.mod = self.mods[-1]

        self.values = {m:{} for m in self.mods}

        for mod in self.mods:
            self.store(mod)

        if self.auto_vgroup:
            self.create_vgroup()

        self.buffer = self.mod.lambda_factor

        #UI System
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


        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif self.base_controls.confirm:
            context.area.header_text_set(text=None)
            self.report({'INFO'}, "Finished")

            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            return {'FINISHED'}

        elif self.base_controls.cancel:
            context.area.header_text_set(text=None)
            self.report({'INFO'}, "Cancelled")
            self.cancel(context)

            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            return {'CANCELLED'}

        if self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        elif self.base_controls.scroll and event.ctrl:
            self.scroll(scroll)
            self.buffer = self.mod.lambda_factor

        elif event.type == 'MOUSEMOVE':

            self.buffer += self.base_controls.mouse
            self.buffer = max(self.buffer, 0)
            digits = 2 if event.ctrl and event.shift else 1 if event.ctrl else 3
            self.mod.lambda_factor = round(self.buffer, digits)

        elif self.base_controls.scroll:
            if event.shift:
                if self.base_controls.scroll ==1 :
                    bpy.ops.object.modifier_move_up(modifier=self.mod.name)
                else:
                    bpy.ops.object.modifier_move_down(modifier=self.mod.name)

            else:
                self.mod.iterations += self.base_controls.scroll

            self.mod.iterations = max(self.mod.iterations, 0)

        elif event.type in ('X', 'Y', 'Z') and event.ctrl:
            if event.type == 'X' and event.value == 'PRESS':
                self.mod.use_x = not self.mod.use_x
            elif event.type == 'Y' and event.value == 'PRESS':
                self.mod.use_y = not self.mod.use_y
            elif event.type == 'Z' and event.value == 'PRESS':
                self.mod.use_z = not self.mod.use_z

        elif event.type in ('X', 'Y', 'Z'):
            if event.type == 'X' and event.value == 'PRESS':
                self.mod.use_x = True
                self.mod.use_y = False
                self.mod.use_z = False
            elif event.type == 'Y' and event.value == 'PRESS':
                self.mod.use_x = False
                self.mod.use_y = True
                self.mod.use_z = False
            elif event.type == 'Z' and event.value == 'PRESS':
                self.mod.use_x = False
                self.mod.use_y = False
                self.mod.use_z = True

        if event.type == "Q" and event.value == "PRESS":
            bpy.ops.object.modifier_move_up(modifier=self.mod.name)

        if event.type == "W" and event.value == "PRESS":
            bpy.ops.object.modifier_move_down(modifier=self.mod.name)


        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def cancel(self, context):
        for mod in self.mods:
            self.reset(mod)

        if self.create_new:
            self.obj.modifiers.remove(self.mods[-1])


    def scroll(self, direction):
        index = self.mods.index(self.mod)
        index = (index + direction) % len(self.mods)
        self.mod = self.mods[index]


    def store(self, mod):
        self.values[mod]["lambda_factor"] = mod.lambda_factor
        self.values[mod]["iterations"] = mod.iterations
        self.values[mod]["use_x"] = mod.use_x
        self.values[mod]["use_y"] = mod.use_y
        self.values[mod]["use_z"] = mod.use_z


    def reset(self, mod):
        mod.lambda_factor = self.values[mod]["lambda_factor"]
        mod.iterations = self.values[mod]["iterations"]
        mod.use_x = self.values[mod]["use_x"]
        mod.use_y = self.values[mod]["use_y"]
        mod.use_z = self.values[mod]["use_z"]


    def create_vgroup(self):
        vertex_group = None

        for group in self.obj.vertex_groups:
            if group.name == "HOPS_L_Smooth":
                vertex_group = group

        if not vertex_group:
            vertex_group = self.obj.vertex_groups.new(name="HOPS_L_Smooth")

        verts = list(range(len(self.obj.data.vertices)))
        vertex_group.add(index=verts, weight=1.0, type='REPLACE')

        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        bevel = bm.edges.layers.bevel_weight.verify()
        crease = bm.edges.layers.crease.verify()

        verts = []
        for v in bm.verts:
            if v.is_boundary:
                verts.append(v.index)
                continue

            for e in v.link_edges:
                if e.seam or not e.smooth or e[bevel] != 0.0 or e[crease] != 0.0:
                    verts.append(v.index)
                    continue

        vertex_group.remove(index=verts)

        self.mod.vertex_group = "HOPS_L_Smooth"


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
            mods = []
            if self.mod.use_x:
                mods.append('X')
            if self.mod.use_y:
                mods.append('Y')
            if self.mod.use_z:
                mods.append('Z')

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(f"{self.mod.iterations}")
                win_list.append(f"{self.mod.lambda_factor:.3f}")
                win_list.append(f"{mods}")
            else:
                win_list.append("Laplacian Smooth")
                win_list.append(f"{self.mod.iterations}")
                win_list.append(f"Factor: {self.mod.lambda_factor:.3f}")
                win_list.append(f"Axis: {mods}")

            # Help
            help_list.append(["Scroll",         "Set iterations"])
            help_list.append(["Shift + Scroll", "Move mod up/down"])
            help_list.append(["X, Y, Z",        "Set axis"])
            help_list.append(["Ctrl + X, Y, Z", "Add axis"])
            help_list.append(["Q",          "Move mod DOWN"])
            help_list.append(["W",          "Move mod UP"])
            help_list.append(["M",         "Toggle mods list."])
            help_list.append(["H",         "Toggle help."])
            help_list.append(["~",         "Toggle viewport displays."])

            # Mods
            if self.mod != None:
                active_mod = self.mod.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="AdjustBevel", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
