import bpy
from bpy.types import Panel

from math import radians
from ... preferences import get_preferences


class HOPS_PT_specialoptions(Panel):
    bl_label = 'General Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        asmooth = bpy.context.object.data
        obj = bpy.context.object
        swire = bpy.context.object
        ob = bpy.context.object

        column = layout.column(align=True)
        row = column.row(align=True)

        column.separator()
        row = column.row(align=True)
        row.prop(obj, "name", text="")

        column.separator()
        row = column.row(align=True)
        row.operator("object.shade_smooth", text="Smooth")
        row.operator("object.shade_flat", text="Flat")

        row = column.row(align=True)
        asmooth = bpy.context.object.data

        if ob.data.has_custom_normals:
            row.prop(asmooth, "use_auto_smooth", text="Auto Smooth", toggle=True)
            row.operator("mesh.customdata_custom_splitnormals_clear", text = "Remove Normal", icon='X')
        else:
            row.prop(asmooth, "use_auto_smooth", text="Auto Smooth", toggle=True)
            row.operator("mesh.customdata_custom_splitnormals_add", text = "Add Normal", icon='ADD')


        column.separator()
        row = column.row(align=True)

        column.separator()
        row = column.row(align=True)
        row.prop(swire, "show_wire", text="Show Wire")
        row.prop(swire, "show_all_edges", text="Show All Wires")

        column.separator()
        row = column.row(align=True)
        row.label(text ="Parent:")
        row.prop(ob, "parent", text="")

        column.separator()
