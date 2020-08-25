import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists


class HOPS_MT_ObjectToolsSubmenu(bpy.types.Menu):
    bl_label = 'Objects Tools Submenu'
    bl_idname = 'HOPS_MT_ObjectToolsSubmenu'

    def draw(self, context):
        layout = self.layout

        if addon_exists('MESHmachine'):
            layout.menu("HOPS_MT_PluginSubmenu", text="Plugin", icon="PLUGIN")

        layout.operator("hops.reset_axis_modal", text="Reset Axis", icon_value=get_icon_id("Xslap"))
        layout.operator("hops.adjust_auto_smooth", text="AutoSmooth", icon_value=get_icon_id("Diagonal"))
        layout.separator()

        layout.operator("hops.bool_dice", text="Dice", icon_value=get_icon_id("Dice"))
        layout.operator("hops.super_array", text="ST3 Array", icon_value=get_icon_id("Display_operators"))
        layout.operator("hops.sphere_cast", text="SphereCast", icon_value=get_icon_id("SphereCast"))

        layout.separator()
        #layout.operator("hops.add_mod_circle_array", text="Circular Array", icon_value=get_icon_id("ArrayCircle"))
        layout.operator("hops.radial_array", text="Radial Array", icon_value=get_icon_id("ArrayCircle"))
        layout.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
        layout.separator()

        layout.operator("hops.apply_modifiers", text="Smart Apply", icon_value=get_icon_id("Applyall")) #.modifier_types='BOOLEAN'

        layout.separator()

        #layout.separator()

        layout.operator("hops.xunwrap", text="Auto Unwrap", icon_value=get_icon_id("CUnwrap"))

        #layout.menu("HOPS_MT_SymmetrySubmenu", text="Symmetry", icon_value=get_icon_id("Xslap"))

        if len(context.selected_objects) == 1:
            #layout.operator("view3d.status_helper_popup", text="HOPS Overide", icon_value=get_icon_id("StatusOveride"))
            layout.operator("hops.reset_status", text="HOPS Reset", icon_value=get_icon_id("StatusReset"))
            layout.separator()


        #layout.operator("hops.add_mod_circle_array", text="Circular Array", icon="PROP_CON").displace_amount = .2
        #layout.operator("hops.twist_apply", text="Twist / Apply 360", icon_value=get_icon_id("ATwist360"))
        #layout.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
        #layout.operator("nw.radial_array", text="Radial 360", icon_value=get_icon_id("ATwist360"))
        #layout.operator("clean.reorigin", text="Apply 360", icon_value=get_icon_id("Applyall")).origin_set = True
        #layout.operator("hops.boolshape_status_swap", text="Green", icon_value=get_icon_id("Green")).red = False

        layout.separator()

        if len(context.selected_objects) == 2:
            layout.operator("hops.shrinkwrap2", text="ShrinkTo", icon_value=get_icon_id("ShrinkTo"))

        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            layout.menu("HOPS_MT_MaterialListMenu", text = "Material List", icon="MATERIAL_DATA")
            if len(context.selected_objects) >= 2:
                layout.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Applyall"))

        layout.menu("HOPS_MT_BoolScrollOperatorsSubmenu", text="Mod Scroll/Toggle", icon_value=get_icon_id("Diagonal"))

        layout.separator()

        #layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")

        #layout.separator()

        layout.menu("HOPS_MT_Export", text = 'Export', icon="EXPORT")


class HOPS_MT_MeshToolsSubmenu(bpy.types.Menu):
    bl_label = 'Mesh Tools Submenu'
    bl_idname = 'HOPS_MT_MeshToolsSubmenu'

    def draw(self, context):
        layout = self.layout
        is_boolean = len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'BOOLEAN'])

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")

        layout.separator()

        layout.operator("hops.bevel_assist", text="Bevel / Edge Manager", icon_value=get_icon_id("CSharpen"))

        layout.separator()

        layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("ModifierHelper"))
        layout.operator("hops.sharp_manager", text="Edge Manager", icon_value=get_icon_id("Diagonal"))
        layout.operator("view3d.bevel_multiplier", text="Bevel Exponent", icon_value=get_icon_id("FaceGrate"))

        layout.separator()

        if is_boolean:
            layout.operator("hops.scroll_multi", text="Bool Multi Scroll ", icon_value=get_icon_id("Diagonal"))
            layout.operator("hops.bool_scroll_objects", text="Object Scroll", icon_value=get_icon_id("StatusReset"))
            layout.separator()

        layout.operator("hops.scroll_multi", text="Mod Scroll/Toggle", icon_value=get_icon_id("StatusReset"))

        op = layout.operator("hops.modifier_scroll", text="Modifier Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.all = True

        layout.operator("hops.bool_toggle_viewport", text= "Toggle Modifiers", icon_value=get_icon_id("Ngons")).all_modifiers = False

        layout.separator()

        layout.menu("HOPS_MT_Export", text = 'Export', icon="EXPORT")
