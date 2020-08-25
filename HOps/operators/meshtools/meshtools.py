import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty
from ... utils.addons import addon_exists
#from ... utils.operations import invoke_individual_resizing
from ... preferences import get_preferences
from ... ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls


class HOPS_OT_VertcircleOperator(bpy.types.Operator):
    bl_idname = "view3d.vertcircle"
    bl_label = "Vert To Circle"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - convert vert to circle
LMB + CTRL - convert nth vert to circle
Shift - Bypass Scale

**Requires Looptools**

"""

    divisions: IntProperty(name="Division Count", description="Amount Of Vert divisions", default=5, )
    radius: FloatProperty(name="Circle Radius", description="Circle Radius", default=0.2)
    message = "< Default >"
    nth_mode: BoolProperty(default=False)


    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"


    def draw(self, context):

        layout = self.layout
        if addon_exists("mesh_looptools"):
            layout.prop(self, "divisions")
            layout.prop(self, "c_offset")
        else:
            layout.label(text = "Looptools is not installed. Enable looptools in prefs")


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context=context, event=event)

        if addon_exists("mesh_looptools"):
            self.c_offset = 40

            #self.divisions = get_preferences().property.circle_divisions
            self.div_past = self.divisions
            self.object = context.active_object

            if event.ctrl:
                bpy.ops.mesh.select_nth()

            bm = bmesh.from_edit_mesh(self.object.data)
            self.backup = bm.copy()
            setup_verts(self.object, self.divisions,  self.c_offset)
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

            if not event.shift:

                #UI System
                self.master = Master(context=context)
                self.master.only_use_fast_ui = True
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}

        else:
            self.report({'INFO'}, "Looptools is not installed. Enable looptools in prefs")

        return {"FINISHED"}


    def modal (self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context=context, event=event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        if self.base_controls.scroll:
            self.divisions += self.base_controls.scroll
            if self.divisions <1 :
                self.divisions = 1
            #collapse_faces (self.object)
            restore(self)
            setup_verts(self.object, self.divisions,  self.c_offset)
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

        elif self.base_controls.mouse:
            if get_preferences().property.modal_handedness == 'LEFT':
                self.radius -= self.base_controls.mouse
            else:
                self.radius += self.base_controls.mouse
            if self.radius <= 0.001:
                 self.radius =0.001
            bpy.ops.mesh.looptools_circle(custom_radius=True, radius = self.radius)

        if self.base_controls.confirm:
            self.master.run_fade()
            return {'FINISHED'}

        if self.base_controls.cancel:
            restore(self)
            self.backup.free
            self.master.run_fade()
            return {'CANCELLED'}

        self.draw_ui(context)

        return {'RUNNING_MODAL'}


    def draw_ui(self, context):

        self.master.setup()

        # -- Fast UI -- #
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append("{:.0f}".format(self.divisions))
                win_list.append("{:.3f}".format(self.radius))
            else:
                win_list.append("Circle")
                win_list.append("Divisions: {:.0f}".format(self.divisions))
                win_list.append("Radius: {:.3f}".format(self.radius))

            # Help
            help_list.append(["LMB", "Apply"])
            help_list.append(["RMB", "Cancel"])
            help_list.append(["Scroll", "Add divisions"])
            help_list.append(["Mouse", "Adjust the radius"])

            # Mods
            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="Tthick", mods_list=mods_list, active_mod_name=active_mod)

        self.master.finished()


def setup_verts(object, divisions,  c_offset):
    '''Set up verts to be converted to circle by loop tools.'''

    bm = bmesh.from_edit_mesh(object.data)
    selected_verts = [v for v in bm.verts if v.select]
    result = bmesh.ops.bevel (bm, geom = selected_verts, vertex_only = True , offset = c_offset,
    loop_slide = True, offset_type = 'PERCENT', clamp_overlap = True, segments = divisions, profile = 0 )
    faces = result['faces']
    faces_clean = bmesh.ops.dissolve_faces (bm, faces = faces)

    for f in faces_clean['region']:
        f.select = True

    bmesh.update_edit_mesh(object.data, destructive = True)


def restore (self):
    '''Reasign original mesh data back to the selected object.'''

    bpy.ops.object.mode_set(mode = 'OBJECT')
    self.backup.to_mesh (self.object. data)
    bpy.ops.object.mode_set( mode = 'EDIT')


# def collapse_faces (object):

#     object = bpy.context.active_object
#     bm = bmesh.from_edit_mesh(object.data)
#     faces = [f for f in bm.faces if f.select]
#     tris = bmesh.ops.poke(bm, faces = faces)

#     edges = []

#     for f in tris['faces']:
#         for e in f.edges:
#             if e not in edges:
#                 edges.append(e)

#     bmesh.ops.collapse (bm, edges = edges)
#     bmesh.update_edit_mesh(object.data, destructive = True)
