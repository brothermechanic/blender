import bpy

from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools


def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)
