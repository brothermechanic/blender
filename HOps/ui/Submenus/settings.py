import os
import bpy
from bpy.types import Menu
from ... icons import get_icon_id
from ... utils.addons import addon_exists


class HOPS_MT_SettingsSubmenu(bpy.types.Menu):
    bl_label = 'Settings Submenu'
    bl_idname = 'HOPS_MT_SettingsSubmenu'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        wm = bpy.context.window_manager
        if hasattr(wm, 'powersave'):
            layout.operator("hops.powersave", text = "PowerSave",  icon_value=get_icon_id("powersave"))

        if bpy.context.space_data.show_region_tool_header == False:
            layout.operator("hops.show_topbar", text = "Show Toolbar")

        #layout.menu("HOPS_MT_MeshToolsSubmenu", text="Helper / Assistant",  icon_value=get_icon_id("SetFrame"))

        layout.operator("hops.learning_popup", text="Hard Ops Learning", icon='HELP')

        layout.separator()

        layout.operator("hops.evict", text="Unify/Evict ", icon_value=get_icon_id("GreyDisplay_dots"))

        layout.separator()

        if context.active_object != None:
            if context.active_object.type == 'CAMERA':
                cam = bpy.context.space_data
                row = layout.row(align=False)
                col = row.column(align=True)

                #col.label(text="Lock Camera To View")
                col.prop(cam, "lock_camera", text="Lock To View")

    #                obj = bpy.context.object.data
    #                col.label(text="Passepartout")
    #                col.prop(obj, "passepartout_alpha", text="")
    #                col.label(text="DOF")
    #                col.prop(obj, "dof_object", text="")
    #                col.label(text="Aperture")
    #                obj = bpy.context.object.data.cycles
    #                col.prop(obj, "aperture_size", text="")
                layout.separator()

        if context.active_object and context.active_object.type == 'MESH':
            #Wire/Solid Toggle
            if context.object.display_type == 'WIRE':
                layout.operator("object.solid_all", text="Shade Solid", icon='MESH_CUBE')
            else :
                layout.operator("showwire.objects", text="Shade Wire", icon='OUTLINER_OB_LATTICE')

#            layout.operator_context = 'INVOKE_DEFAULT'
#            layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

#            if pro_mode_enabled():
#                layout.operator("hops.viewport_buttons", text="Dots", icon_value=get_icon_id("dots"))

#            if len(context.selected_objects) == 1:
#                layout.menu("HOPS_MT_BasicObjectOptionsSubmenu", text="Object Options")

        view = context.space_data
        layout.prop(view.overlay, 'show_wireframes')

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.adjust_viewport", text="LookDev+", icon_value=get_icon_id("RGui"))

        #Viewport Submenu
        layout = self.layout

        layout = self.layout
        try:
            scene = context.scene.cycles
        except:
            pass

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.separator()

        #Voxelization Addition 2.81
        if context.active_object and context.active_object.type == 'MESH':

            layout.prop(context.active_object.data, 'remesh_voxel_size', text='Voxel Size')

            layout.operator("view3d.voxelizer", text=F"Voxelize Object", icon_value=get_icon_id("Voxelize"))

            layout.separator()

        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)

        #col.prop(scene, 'frame_end')

        layout.menu("HOPS_MT_FrameRangeSubmenu", text="Frame Range Options",  icon_value=get_icon_id("SetFrame"))

        layout.separator()

        #Order Pizza Button Haha
        layout.operator("view3d.pizzapopup", text="Pizza Ops", icon_value=get_icon_id("Pizzaops"))

        #layout.separator()
        #layout.menu("HOPS_MT_Export", text = 'Export', icon_value=get_icon_id("Tris"))

        layout.separator()

        # if bpy.context.object and bpy.context.object.type == 'MESH':
        #     layout.menu("HOPS_MT_MaterialListMenu", text = "Material List", icon_value=get_icon_id("StatusOveride"))
        if context.active_object and context.active_object.type == 'MESH':
            layout.menu("HOPS_MT_SelectViewSubmenu", text="Selection Options",  icon_value=get_icon_id("ShowNgonsTris"))

        layout.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("WireMode"))

        layout.separator()
        layout.operator("hops.about", text = "About",  icon_value=get_icon_id("sm_logo_white"))
        
        # ot = layout.operator("hops.display_notification", text="Notification")
        # ot.info = "Test Is working"

        