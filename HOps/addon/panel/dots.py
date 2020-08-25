import bpy
from bpy.types import Panel

from bl_ui.properties_data_modifier import DATA_PT_modifiers as modifier


class HARDFLOW_PT_dots(Panel):
    bl_label = 'Modifier'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOL_HEADER'


    def draw(self, context):
        hardflow = bpy.context.window_manager.hardflow

        obj = context.active_object

        layout = self.layout
        layout.ui_units_x = 15

        layout.label(text=hardflow.dots.description)

        if hardflow.dots.mod:
            mod = obj.modifiers[hardflow.dots.mod]
            box = layout.template_modifier(mod)

            if box:
                getattr(modifier, mod.type)(modifier, box, obj, mod)
