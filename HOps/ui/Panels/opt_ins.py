import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_opt_ins(Panel):
    bl_label = 'Opt-In Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences().property
        color = get_preferences().color
        ui = get_preferences().ui

        column = layout.column(align=True)

        row = column.row(align=True)

        column.separator()
        row = column.row(align=True)
        row.prop(color, 'Hops_UI_cell_background_color', text='Modal BG Color')
        column.separator()
        row = column.row(align=True)
        row.prop(ui, 'Hops_operator_display', text='Operator Text Display')
        row = column.row(align=True)
        row.label(text='Modal Help Scale:')
        row.prop(ui, 'Hops_modal_fast_ui_help_size', text='')
        row = column.row(align=True)
        row.label(text='Bevel Profile:')
        #row = column.row(align=True)
        row.prop(preference, 'bevel_profile', text='')
        row = column.row(align=True)
        row.label(text='Modal Handedness')
        #row = column.row(align=True)
        row.prop(preference, 'modal_handedness', text='')
        row = column.row(align=True)
        row.label(text='Q Menu Array Type')
        row.prop(preference, 'menu_array_type', text='')
        if get_preferences().property.menu_array_type == 'ST3':
            row = column.row(align=True)
            row.label(text='ST3 Array Gizmo Type')
            row.prop(preference, 'array_type', text='')
        column.separator()
        row = column.row(align=True)
        row.prop(get_preferences().behavior, 'mat_viewport', text='Blank Mat similar to Viewport ')
        row = column.row(align=True)
        row.prop(preference, 'Hops_twist_radial_sort', text='Radial/Twist (Render/Edit Toggle)')
        row = column.row(align=True)
        row.prop(preference, 'to_cam_jump', text='To_Cam Jump')
        row = column.row(align=True)
        row.prop(preference, 'to_render_jump', text='Viewport+ Set Render')
        row = column.row(align=True)
        # row.prop(preference, 'sort_modifiers', text='Sort Modifier System', expand=True)
        # row = column.row(align=True)
        #row.prop(preference, 'st3_meshtools', text='ST3 Meshtools Unlock')
