import bpy, bmesh
from ...ui_framework.operator_ui import Master
from ... preferences import get_preferences, get_addon_name


class HOPS_OT_Edge2Curve(bpy.types.Operator):
    bl_idname = "hops.edge2curve"
    bl_label = "Converts Edge To Curve"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Converts edge to curve.
LMB+SHIFT - Converts selection into plate.
LMB+CTRL - New object from selection.
ALT - Destructive extract
"""

    called_ui = False

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'


    def invoke(self, context, event):
        HOPS_OT_Edge2Curve.called_ui = False
        self.original_active = context.active_object
        self.mode = "Curve"
        self.destructive = False
        if event.shift and not event.ctrl:
            self.mode = "Plate"
        if event.ctrl and not event.shift:
            self.mode = "Piece"
        if event.alt:
            self.destructive = True
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        bm= bmesh.new()
        result =""
        deselect_geom =[]
        if obj.mode == 'EDIT':
            obj.update_from_editmode()
            bm.from_mesh(obj.data)
            if self.mode == "Curve":
                if bm.edges:
                    deselect_geom = [e for e in bm.edges if not e.select]
                    bm_context = 'EDGES'

            if self.mode == "Plate":
                if bm.faces:
                    deselect_geom = [f for f in bm.faces if not f.select]
                    bm_context = 'FACES'

            if self.mode == "Piece":
                if bm.verts:
                    select_mode = bpy.context.tool_settings.mesh_select_mode
                    if select_mode[0]:
                        deselect_geom = [v for v in bm.verts if not v.select]
                        bm_context = 'VERTS'
                    if select_mode[1]:
                        deselect_geom = [e for e in bm.edges if not e.select]
                        bm_context = 'EDGES'
                    if select_mode[2] and bm.faces:
                        deselect_geom = [f for f in bm.faces if not f.select]
                        bm_context = 'FACES'
            if bm_context == 'FACES':
                floaters = [f for f in bm.verts if not f.link_faces ]
                bmesh.ops.delete(bm, geom= floaters, context= 'VERTS')

        else:
            bm.from_mesh(obj.data)
            if self.mode == "Plate":
                floaters = [f for f in bm.verts if not f.link_faces ]
                bmesh.ops.delete(bm, geom= floaters, context= 'VERTS')

        if deselect_geom:
            bmesh.ops.delete(bm, geom= deselect_geom, context= bm_context)
                            
            if self.destructive:
                bm_edit = bmesh.from_edit_mesh(obj.data)
                selected_geom = [f for f in bm_edit.faces if f.select ]
                bmesh.ops.delete(bm_edit, geom= selected_geom, context= 'FACES')
                if bm_context != 'FACES':
                    floaters = [f for f in bm_edit.verts if f.select and not f.link_faces  ]
                    bmesh.ops.delete(bm_edit, geom= floaters, context= 'VERTS')


        if not bm.verts or (self.mode == "Plate" and not bm.faces) :
            result="Cancelled. No valid selection"

        if not result:
            new_mesh = obj.data.copy()
            new_mesh.name = F"{obj.data.name}_{self.mode}"
            bm.to_mesh(new_mesh)
            bm.free()
            curve_obj= obj.copy()
            curve_obj.name = F"{obj.name}_{self.mode}"
            curve_obj.data = new_mesh
            for col in obj.users_collection:
                col.objects.link(curve_obj)
            for o in bpy.context.selected_objects:
                if o != curve_obj:
                    o.select_set(0)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = curve_obj
            bpy.ops.hops.reset_status()
            mod = None

            for mod in curve_obj.modifiers:
                if mod.type in {'WEIGHTED_NORMAL'}:
                    curve_obj.modifiers.remove(mod)

            bpy.context.object.data.use_auto_smooth = True
            
            result = "Success"
            if self.mode == "Plate":
                bpy.ops.hops.adjust_tthick('INVOKE_DEFAULT')

            if self.mode == "Curve":
                bpy.ops.object.convert(target='CURVE')
                if context.active_object.type == 'CURVE':
                    bpy.ops.hops.adjust_curve('INVOKE_DEFAULT')
                else:
                    bpy.ops.object.convert(target='MESH')
                    bm = bmesh.new()
                    bm.from_mesh(curve_obj.data)
                    bmesh.ops.delete(bm, geom = bm.faces, context= 'FACES_ONLY')
                    bm.to_mesh(curve_obj.data)
                    bm.free()
                    bpy.ops.object.convert(target='CURVE')
                    if context.active_object.type == 'CURVE':
                        bpy.ops.hops.adjust_curve('INVOKE_DEFAULT')
                    else:
                        result = "Failed. Selection is too complex"
                        bpy.data.objects.remove(curve_obj)
                        context.view_layer.objects.active = self.original_active
                        self.original_active.select_set(True)

        # Operator UI
        if not HOPS_OT_Edge2Curve.called_ui:
            HOPS_OT_Edge2Curve.called_ui = True

            ui = Master()
            draw_data = [
                ["To_" + self.mode],
                [result],
                [F"Converted to {self.mode}"]
                ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)


        return {"FINISHED"}
