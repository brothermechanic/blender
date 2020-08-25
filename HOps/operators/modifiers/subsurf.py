import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master

class HOPS_OT_MOD_Subdivision(bpy.types.Operator):
    bl_idname = "hops.mod_subdivision"
    bl_label = "Add Subdivision Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Subdivision Modifier
LMB + Shift - Use Simple Option
LMB + CTRL - Add new Subdivision Modifier

"""
    sub_d_level: bpy.props.IntProperty(
        name="Sub-d Level",
        description="Amount Of Sub-d to add",
        default=2)

    called_ui = False

    def __init__(self):

        HOPS_OT_MOD_Subdivision.called_ui = False

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def draw(self, context):
        self.layout.prop(self, "sub_d_level")

    def invoke(self, context, event):
        for object in [o for o in context.selected_objects if o.type == 'MESH']:
            if event.ctrl:
                self.add_Subdivision_modifier(object, self.sub_d_level, event)
            else:
                if not self.Subdivision_modifiers(object):
                    self.add_Subdivision_modifier(object, self.sub_d_level, event)
        # Operator UI
        if not HOPS_OT_MOD_Subdivision.called_ui:
            HOPS_OT_MOD_Subdivision.called_ui = True

            ui = Master()
            draw_data = [
                ["SUBDIVISION"],
                ["Subdivision Level", self.sub_d_level]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

    def execute(self, context):
        return {"FINISHED"}


    @staticmethod
    def Subdivision_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SUBSURF"]

    def add_Subdivision_modifier(self, object, sub_d_level, event):
        subsurf_mod = object.modifiers.new(name="Subdivision", type="SUBSURF")
        if event.shift:
            subsurf_mod.subdivision_type = 'SIMPLE'
        else:
            subsurf_mod.subdivision_type = 'CATMULL_CLARK'
            subsurf_mod.levels = sub_d_level
