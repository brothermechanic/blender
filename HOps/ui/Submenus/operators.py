import bpy
import math
from ... icons import get_icon_id
from ... utils.addons import addon_exists


class HOPS_MT_ObjectsOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Object Mode

    """
    bl_label = 'Objects Operators Submenu'
    bl_idname = 'HOPS_MT_ObjectsOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = layout.row(align=False)
        col = row.column(align=True)

        object = context.active_object

        layout.operator_context = 'INVOKE_DEFAULT'
        ot = layout.operator("hops.modifier_scroll", text="Modifier Scroll", icon_value=get_icon_id("Tris"))
        ot.all=True
        ot.additive=True

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.bevel_assist", text="Bevel / Edge Manager", icon_value=get_icon_id("CSharpen"))
        #layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("CSharpen"))



        layout.separator()

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.sharpen", text="Sharpen", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))
        layout.separator()

        if addon_exists("MESHmachine"):
            layout.separator()
            layout.menu("MACHIN3_MT_mesh_machine", text="MESHmachine", icon_value=get_icon_id("Machine"))

        layout.separator()
        layout.operator("hops.to_shape", text="To_Shape", icon_value=get_icon_id("Display_boolshapes"))
        #layout.operator("hops.to_plane", text="To_Plane", icon_value=get_icon_id("Booleans"))
        layout.operator("hops.edge2curve", text="Curve/Extract", icon_value=get_icon_id("Curve"))

        layout.separator()

        layout.operator("hops.camera_rig", text="Add Camera", icon='OUTLINER_OB_CAMERA')
        layout.operator("hops.blank_light", text="Add Lights", icon='LIGHT')

        layout.separator()

        layout.operator("hops.apply_modifiers", text="Smart Apply", icon_value=get_icon_id("Applyall")) #.modifier_types='BOOLEAN'

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("view3d.clean_mesh", text="Clean Mesh", icon_value=get_icon_id("FaceGrate"))

        layout.separator()

        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array (gizmo)", icon_value=get_icon_id("Qarray"))

        layout.separator()

        #layout.operator_context = 'INVOKE_DEFAULT'
        #layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))

        #layout.separator()

        
        layout.separator()

        #layout.operator("hops.adjust_bevel", text="Bevel", icon_value=get_icon_id("AdjustBevel"))

        layout.separator()

        #layout.label(text = "____2.8 Gizmos")

#        for mod in object.modifiers:
#            if mod.type == "BEVEL":
#                col.prop(object.modifiers['Bevel'], "segments")
#                col.separator()

        # if len(context.selected_objects) == 1:
        #if context.active_object.hops.status == 'BOOLSHAPE':
        is_boolean = len([mod for mod in bpy.context.active_object.modifiers if mod.type == 'BOOLEAN'])
        if is_boolean:
            layout.separator()
            layout.operator("hops.late_parent", text="Late Parent", icon_value=get_icon_id("Tris"))
        if context.active_object.hops.status == 'BOOLSHAPE':
            layout.separator()
            layout.operator("hops.late_paren_t", text="Late Parent", icon_value=get_icon_id("Tris"))
        #layout.operator_context = 'INVOKE_DEFAULT'
        #layout.operator("hops.clearclean", text="Clean / Clear Mesh", icon_value=get_icon_id("CleansharpsE"))
        layout.operator("clean.sharps", text="Clear Sharps", icon_value=get_icon_id("CleansharpsE"))

        layout.separator()

        layout.menu("HOPS_MT_ModSubmenu", text="Add Modifier", icon_value=get_icon_id("Diagonal"))

class HOPS_MT_MeshOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Edit Mode

    """
    bl_label = 'Mesh Operators Submenu'
    bl_idname = 'HOPS_MT_MeshOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.menu("HOPS_MT_ModSubmenu", text = 'Add Modifier',  icon_value=get_icon_id("Tris"))
        layout.separator()
        layout.operator("hops.bevel_weight", text="Adjust Bevel Weight", icon_value=get_icon_id("AdjustBevel"))
        layout.operator("hops.meshdisp", text="Display Marks", icon="PLUGIN")
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        #layout.separator()
        #layout.operator("hops.set_edit_sharpen", text="Set SSharp", icon_value=get_icon_id("MakeSharpE"))
        #layout.separator()
        #layout.operator("clean1.objects", text="Clean SSharps", icon_value=get_icon_id("CleansharpsE"))

        layout.separator()

        #layout.operator_context = 'EXEC_DEFAULT'
        op = layout.operator("mesh.spin", text = 'Spin')
        op.steps = 6
        op.angle = 6.28319
        #if event.ctrl:
        #    op.axis =( 0, 1, 0)
        #else:
        #    pass

        layout.separator()

        layout.operator("hops.edge2curve", text="Curve/Extract", icon_value=get_icon_id("Curve"))
        layout.operator("hops.to_shape", text="To_Shape", icon_value=get_icon_id("Display_boolshapes"))
        #layout.operator("hops.to_plane", text="To_Plane", icon_value=get_icon_id("Booleans"))
        layout.separator()
        layout.menu("HOPS_MT_EditClassicsSubmenu", text = 'Meshtools',  icon_value=get_icon_id("Tris"))
        layout.operator("view3d.vertcircle", text="Circle", icon_value=get_icon_id("NthCircle"))
        layout.operator("hops.to_shape", text="To_Shape", icon_value=get_icon_id("Display_boolshapes"))
        layout.operator("hops.reset_axis_modal", text="Reset Axis / Flatten", icon_value=get_icon_id("Xslap"))
        #layout.operator("view3d.vertcircle", text="Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True
        #layout.operator("hops.circle", text="NEW Circle", icon_value=get_icon_id("NthCircle"))
        #layout.separator()
        layout.separator()
        layout.operator("hops.star_connect", text="Star Connect", icon_value=get_icon_id("Machine"))
        layout.operator("clean1.objects", text="Demote", icon_value=get_icon_id("Demote")).clearsharps = False
        # if any("mira_tools" in s for s in bpy.context.preferences.addons.keys()):
        #     layout.separator()
        #     layout.menu("HOPS_MT_MiraSubmenu", text="Mira (T)", icon="PLUGIN")
        # else:
        #     layout.separator()

        if addon_exists("MESHmachine"):
            layout.separator()
            layout.menu("MACHIN3_MT_mesh_machine", text="MESHmachine", icon_value=get_icon_id("Machine"))

        if len(bpy.context.selected_objects) == 2:
            layout.separator()
            layout.operator("object.to_selection", text="Obj To Selection", icon_value=get_icon_id("dots"))
            layout.separator()

        layout.menu("HOPS_MT_PluginSubmenu", text="Plugin", icon="PLUGIN")
        layout.separator()
        #layout.operator("hops.reset_axis", text="Reset Axis / Flatten", icon_value=get_icon_id("Xslap"))

        layout.menu("HOPS_MT_BoolSumbenu", text="Booleans", icon="MOD_BOOLEAN")
        layout.operator("view3d.clean_mesh", text="Clean Mesh", icon_value=get_icon_id("CleansharpsE"))
        #layout.separator()

class HOPS_MT_MergeOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for merging insert meshes.

    """
    bl_label = 'Merge Operators Submenu'
    bl_idname = 'HOPS_MT_MergeOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge", text="(C) merge")#, icon_value=get_icon_id("Merge"))
        layout.operator("hops.parent_merge_soft", text="(C) merge(soft)", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.simple_parent_merge", text="(S) merge")#, icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text="Remove Merge")#, icon_value=get_icon_id("Merge"))

class HOPS_MT_EditClassicsSubmenu(bpy.types.Menu):
    """
    Operations Edit Mesh Operators Submenu

    """
    bl_label = 'Edit Mesh Operators Submenu'
    bl_idname = 'HOPS_MT_EditClassicsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator("fgrate.op", text="Grate (Face)", icon_value=get_icon_id("FaceGrate"))
        layout.operator("fknurl.op", text="Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))
        layout.separator()

        layout.operator("quick.panel", text="Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))
        layout.operator("entrench.selection", text="Panel (Edge)", icon_value=get_icon_id("FacePanel"))

class HOPS_MT_BoolScrollOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for bool scroll stuff

    """
    bl_label = 'Bool Scroll Operators Submenu'
    bl_idname = 'HOPS_MT_BoolScrollOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        op = layout.operator("hops.modifier_scroll", text="Modifier Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.all = True

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.bool_scroll_objects", text="Object Scroll", icon_value=get_icon_id("StatusReset"))

        op = layout.operator("hops.modifier_scroll", text="Cycle Booleans", icon_value=get_icon_id("StatusOveride"))
        op.additive = False
        op.type = 'BOOLEAN'

        op = layout.operator("hops.modifier_scroll", text="Additive Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.type = 'BOOLEAN'

        layout.separator()

        layout.operator("hops.scroll_multi", text="Bool/Mod Scroll/Toggle", icon_value=get_icon_id("StatusReset"))

        layout.separator()

        layout.operator("hops.bool_toggle_viewport", text= "Toggle Modifiers", icon_value=get_icon_id("Tris")).all_modifiers = False
