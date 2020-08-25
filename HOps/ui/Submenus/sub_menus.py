import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import get_preferences

class HOPS_MT_Export(bpy.types.Menu):
    bl_idname = "HOPS_MT_Export"
    bl_label = "Export Options"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        box = layout.column(align=True)

        ot = box.operator("export_scene.obj", text="OBJ")
        ot.use_selection = True
        ot.use_triangles = True

        ot = box.operator("export_scene.fbx", text="FBX")
        ot.use_selection = True

        ot = box.operator("wm.alembic_export", text="ABC")
        ot.selected = True

# Material
class HOPS_MT_MaterialListMenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_MaterialListMenu"
    bl_label = "Material list"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        object = context.active_object

        filepathprefs = bpy.context.preferences.filepaths

        # draw dot name toggle at the top of the menu
        col.prop(filepathprefs, 'show_hidden_files_datablocks', text="hide .names")

        col.separator()
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator("material.hops_new", text = 'Add Blank Material', icon="PLUS")
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator("hops.material_scroll", text = 'Material Scroll', icon_value=get_icon_id("StatusReset"))
        if len(context.selected_objects) >= 2:
            if object.material_slots:
                col.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Applyall"))
        else:
            col.separator()

        # filter out dot name materials, based on blender prefs
        materials = [mat for mat in bpy.data.materials if not mat.name.startswith('.')] if filepathprefs.show_hidden_files_datablocks else bpy.data.materials

        if materials:
            col.separator()

            for mat in materials:
                try:
                    icon_val = layout.icon(mat)
                except:
                    icon_val = 1
                    print("WARNING [Mat Panel]: Could not get icon value for %s" % mat.name)

                op = col.operator("object.apply_material", text=mat.name, icon_value=icon_val)
                op.mat_to_assign = mat.name


class HOPS_MT_SculptSubmenu(bpy.types.Menu):
    bl_label = 'Sculpt'
    bl_idname = 'HOPS_MT_SculptSubmenu'

    def draw(self, context):
        layout = self.layout

        # sculpt = context.tool_settings.sculpt
        # settings = self.paint_settings(context)
        # brush = settings.brush

        if context.sculpt_object.use_dynamic_topology_sculpting:
            layout.operator("sculpt.dynamic_topology_toggle",text="Disable Dyntopo")
        else:
            layout.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo")
        layout.separator()

        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.prop(context.tool_settings.sculpt, "constant_detail")
            layout.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        elif (context.tool_settings.sculpt.detail_type_method == 'BRUSH'):
            layout.prop(context.tool_settings.sculpt, "detail_percent")
        else:
            layout.prop(context.tool_settings.sculpt, "detail_size")
        layout.prop(context.tool_settings.sculpt, "detail_refine_method", text="")
        layout.prop(context.tool_settings.sculpt, "detail_type_method", text="")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "use_smooth_shading")
        layout.operator("sculpt.optimize")
        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.operator("sculpt.detail_flood_fill")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "symmetrize_direction", text="")
        layout.operator("sculpt.symmetrize")


class HOPS_MT_MiraSubmenu(bpy.types.Menu):
    bl_label = 'Mira Panel'
    bl_idname = 'HOPS_MT_MiraSubmenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout.column_flow(columns=2)

        # if mira_handler_enabled():
        #     layout.operator("mesh.curve_stretch", text="CurveStretch", icon="RNA")
        #     layout.operator("mesh.curve_guide", text='CurveGuide', icon="RNA")


        layout.operator("mira.curve_stretch", text="CurveStretch", icon="RNA")
        layout.operator("mira.curve_guide", text="CurveGuide", icon="RNA")
        layout.prop(context.scene.mi_cur_stretch_settings, "points_number", text='')
        layout.prop(context.scene.mi_curguide_settings, "points_number", text='')


class HOPS_MT_BasicObjectOptionsSubmenu(bpy.types.Menu):
    bl_label = 'ObjectOptions'
    bl_idname = 'HOPS_MT_BasicObjectOptionsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout.column_flow(columns=1)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.2

        obj = bpy.context.object

        layout.prop(obj, "name", text="")
        layout.separator()

        obj = bpy.context.object

        layout.prop(obj, "show_name", text="Show object's name"),


class HOPS_MT_FrameRangeSubmenu(bpy.types.Menu):
    bl_label = 'FrameRange'
    bl_idname = 'HOPS_MT_FrameRangeSubmenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.operator("setframe.end", text="Frame Range", icon_value=get_icon_id("SetFrame"))

        col.prop(scene, 'frame_start')
        col.prop(scene, 'frame_end')


class HOPS_MT_SelectViewSubmenu(bpy.types.Menu):
    bl_label = 'Selection'
    bl_idname = 'HOPS_MT_SelectViewSubmenu'

    def draw(self, context):
        layout = self.layout

        m_check = context.window_manager.m_check

        if bpy.context.object and bpy.context.object.type == 'MESH':
            if m_check.meshcheck_enabled:
                layout.operator("object.remove_materials", text="Hidde Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))
            else:
                layout.operator("object.add_materials", text="Display Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))

            layout.operator("data.facetype_select", text="Ngons Select", icon_value=get_icon_id("Ngons")).face_type = "5"
            layout.operator("data.facetype_select", text="Tris Select", icon_value=get_icon_id("Tris")).face_type = "3"

# Viewport


class HOPS_MT_ViewportSubmenu(bpy.types.Menu):
    bl_label = 'Viewport'
    bl_idname = 'HOPS_MT_ViewportSubmenu'

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        c = bpy.context.scene


        #layout.operator("ui.reg", text="Normal", icon_value=get_icon_id("NGui"))
        #layout.operator("ui.clean", text="Minimal", icon_value=get_icon_id("QGui"))
        layout.prop(view.overlay, "show_overlays", text = 'Overlays')
        layout.prop(view.overlay, 'show_wireframes')
        layout.prop(view.overlay, 'show_face_orientation')
        layout.operator("hops.camera_rig", text="Add Camera", icon='OUTLINER_OB_CAMERA')
        if c.render.engine == 'BLENDER_EEVEE':
            layout.separator()
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.adjust_viewport", text="(v)Lookdev+", icon_value=get_icon_id("RGui"))
            layout.operator("render.setup", text="Eevee HQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Eevee LQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("ui.reg", text="Solid / Texture Toggle", icon="RESTRICT_RENDER_OFF")
        if c.render.engine == 'CYCLES':
            layout.separator()
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.adjust_viewport", text="Lookdev+", icon_value=get_icon_id("RGui"))
            layout.operator("render.setup", text="Cycles HQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Cycles LQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderc.setup", text="GPU HQ ", icon="RESTRICT_RENDER_OFF")
        else:
            pass

        if addon_exists("Fidget"):
            layout.separator()
            row = layout.row()
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator("fidget.viewport_buttons", text="Fidget")

        if c.render.engine == 'BLENDER_EEVEE' or c.render.engine == 'CYCLES':
            layout.separator()
            layout.prop(view.shading, "type", text = "")
            if view.shading.type != 'WIREFRAME':
                layout.separator()
            if view.shading.type == 'SOLID':
                layout.prop(view.shading, "light", text = "")
                layout.prop(view.shading, "color_type", text = "")
                layout.separator()
            if view.shading.type != 'WIREFRAME' and view.shading.type != 'RENDERED':
                if view.shading.light in ["STUDIO", "MATCAP"]:
                    layout.template_icon_view(view.shading, "studio_light", show_labels=True, scale=3)
                    layout.separator()
            if view.shading.type == 'MATERIAL' or view.shading.type == 'RENDERED':
                layout.prop(bpy.context.scene.eevee, "use_ssr", text = "Screen Space Reflections")
                if bpy.context.scene.eevee.use_ssr == True:
                    layout.prop(bpy.context.scene.eevee, "use_ssr_halfres", text = "Half Res")
                layout.prop(bpy.context.scene.eevee, "use_gtao", text = "AO")
                #layout.prop(bpy.context.scene.eevee, "use_dof", text = "DOF")
                layout.prop(bpy.context.scene.eevee, "use_bloom", text = "Bloom")
                layout.prop(bpy.context.scene.eevee, "use_soft_shadows", text = "Soft Shadows")
                layout.prop(bpy.context.scene.eevee, "gi_diffuse_bounces", text = "Indirect Bounces")
                layout.prop(bpy.context.scene.eevee, "taa_samples", text = "Viewport Samples")
                layout.separator()
            if view.shading.type == 'MATERIAL':
                layout.prop(view.shading, 'use_scene_lights')
                layout.prop(view.overlay, 'show_look_dev')
            if view.shading.type == 'SOLID':
                if view.overlay.show_overlays == True:
                    layout.prop(view.overlay, 'wireframe_threshold')
                    layout.separator()
                layout.prop(bpy.context.scene.eevee, "use_gtao", text = "AO")
                layout.prop(bpy.context.scene.eevee, "use_soft_shadows", text = "Soft Shadows")
                layout.separator()
                layout.prop(view.shading, 'show_cavity')
                layout.prop(view.shading, 'show_shadows')
            #layout.separator()
            #layout.label(text = view.shading.type)
            layout.separator()
            if bpy.context.space_data.show_region_tool_header == False:
                layout.operator("hops.show_topbar", text = "Show Toolbar")
            layout.separator()
            layout.operator("hops.blank_light", text = "Blank Light", icon_value=get_icon_id("GreyTaper"))


class HOPS_MT_RenderSetSubmenuLQ(bpy.types.Menu):
    bl_label = 'RenderSet_submenu_LQ'
    bl_idname = 'HOPS_MT_RenderSetSubmenuLQ'

    def draw(self, context):
        layout = self.layout
        layout.prop(get_preferences().property, "Eevee_preset_LQ", expand=True)


class HOPS_MT_RenderSetSubmenuHQ(bpy.types.Menu):
    bl_label = 'RenderSet_submenu_HQ'
    bl_idname = 'HOPS_MT_RenderSetSubmenuHQ'

    def draw(self, context):
        layout = self.layout
        layout.prop(get_preferences().property, "Eevee_preset_HQ", expand=True)


class HOPS_MT_RenderSetSubmenu(bpy.types.Menu):
    bl_label = 'RenderSet_submenu'
    bl_idname = 'HOPS_MT_RenderSetSubmenu'

    def draw(self, context):
        layout = self.layout

        c = bpy.context.scene
        if c.render.engine == 'CYCLES':
            layout.operator("render.setup", text="Render (1)", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Render (2)", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderc.setup", text="Cycles GPU HQ Grumble", icon="RESTRICT_RENDER_OFF")
        if c.render.engine == 'BLENDER_EEVEE':
            layout.operator("render.setup", text="Eevee HQ", icon="RESTRICT_RENDER_OFF")
            layout.menu("HOPS_MT_RenderSetSubmenuHQ", text="HQ Settings")
            layout.operator("renderb.setup", text="Eevee LQ", icon="RESTRICT_RENDER_OFF")
            layout.menu("HOPS_MT_RenderSetSubmenuLQ", text="LQ Settings")
        else:
            pass

        layout.separator()

        row = layout.row(align=False)
        col = row.column(align=True)

        view_settings = context.scene.view_settings
        col.prop(view_settings, "view_transform", text="")
        col.prop(view_settings, "look", text="")


class HOPS_MT_ResetAxiSubmenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_ResetAxiSubmenu"
    bl_label = "Reset Axis Submenu"

    def draw(self, context):
        layout = self.layout
        #layout = self.layout.column_flow(columns=2)
        #row = layout.row()
        #sub = row.row()
        #sub.scale_y = 1.0
        #sub.scale_x = 0.05

        layout.operator("hops.reset_axis", text=" X ", icon_value=get_icon_id("Xslap")).set_axis = "X"
        layout.operator("hops.reset_axis", text=" Y ", icon_value=get_icon_id("Yslap")).set_axis = "Y"
        layout.operator("hops.reset_axis", text=" Z ", icon_value=get_icon_id("Zslap")).set_axis = "Z"


class HOPS_MT_SymmetrySubmenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_SymmetrySubmenu"
    bl_label = "Symmetry Submenu"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))

class HOPS_MT_MiscSubmenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_MiscSubmenu"
    bl_label = "Misc Submenu"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.separator()
        layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.sharp_manager", text="Edge Manager", icon_value=get_icon_id("Diagonal"))
        layout.operator("view3d.bevel_multiplier", text="Bevel Exponent", icon_value=get_icon_id("BevelMultiply"))

class HOPS_MT_PluginSubmenu(bpy.types.Menu):
    bl_label = 'Plugin Tools Submenu'
    bl_idname = 'HOPS_MT_PluginSubmenu'

    def draw(self, context):
        layout = self.layout

        #        if any("kk_QuickLatticeCreate" in s for s in bpy.context.preferences.addons.keys()):
        #            layout.operator("object.easy_lattice", text="Easy Lattice", icon_value=get_icon_id("Easylattice"))

        #        if any("mesh_snap" in s for s in bpy.context.preferences.addons.keys()):
        #            layout.operator("mesh.snap_utilities_line", text="Snap Line")
        #            layout.operator("mesh.snap_push_pull", text="Push Pull Faces")

        object = context.active_object

        if object.mode == "EDIT" and object.type == "MESH":
            if addon_exists('mira_tools'):
                layout.label(text = "Mira Tools")
                layout.separator()
                op = layout.operator("mesh.curve_stretch", text="Curve Stretch")#,
                layout.operator("mira.curve_stretch", text="MI_CurveStretch", icon="STYLUS_PRESSURE")
                layout.prop(bpy.context.scene.mi_cur_stretch_settings, "points_number", text='Curve Count')
                layout.separator()
            if addon_exists('bezier_mesh_shaper'):
                layout.separator()
                layout.label(text = "Bezier Mesh Shaper")
                layout.separator()
                op = layout.operator("mesh.bezier_mesh_shaper", text="Curved")#, icon_value=get_icon_id("Easylattice"))
                op.startupAction = 'NORMAL'

                op = layout.operator("mesh.bezier_mesh_shaper", text="Straight")#, icon_value=get_icon_id("Easylattice"))
                op.startupAction ='SNAP_STRAIGHT'
                layout.separator()

        if object.mode == "OBJECT" or object.mode == "EDIT":
            if addon_exists("MESHmachine"):
                layout.label(text = "MeshMachine")
                layout.separator()
                layout.menu("MACHIN3_MT_mesh_machine", text="MESHmachine", icon_value=get_icon_id("Machine"))
                layout.separator()


class HOPS_MT_BoolSumbenu(bpy.types.Menu):
    bl_label = 'Bool Submenu'
    bl_idname = 'HOPS_MT_BoolSumbenu'

    def draw(self, context):
        layout = self.layout

        object = context.active_object

        if object.mode == "OBJECT" and object.type == "MESH":
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.bool_modal", text="Interactive Boolean", icon_value=get_icon_id("InteractiveBoolean"))
            layout.separator()
            layout.operator("hops.bool_difference", text="Difference", icon_value=get_icon_id("Difference"))
            layout.operator("hops.bool_union", text="Union", icon_value=get_icon_id("Union"))
            layout.operator("hops.slash", text="Slash", icon_value=get_icon_id("Slash"))
            layout.separator()
            layout.operator("hops.bool_inset", text="Inset / Outset", icon_value=get_icon_id("InsetOutset"))
            layout.operator("hops.bool_knife", text="Knife", icon_value=get_icon_id("Knife"))
            layout.operator("hops.bool_intersect", text="Intersection", icon_value=get_icon_id("Intersection"))
            layout.separator()
            layout.operator("hops.cut_in", text="Cut-in", icon_value=get_icon_id("Cutin"))

        if object.mode == "EDIT" and object.type == "MESH":
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.bool_modal", text="Interactive Boolean", icon_value=get_icon_id("InteractiveBoolean"))
            layout.operator("hops.selection_to_boolean", text="Selection to Boolean", icon="MOD_BOOLEAN")
            layout.separator()
            layout.operator("hops.edit_bool_difference", text="Difference", icon_value=get_icon_id("Difference"))
            layout.operator("hops.edit_bool_union", text="Union", icon_value=get_icon_id("Union"))
            layout.operator("hops.edit_bool_slash", text="Slash", icon_value=get_icon_id("Slash"))
            layout.separator()
            layout.operator("hops.edit_bool_inset", text="Inset / Outset", icon_value=get_icon_id("InsetOutset"))
            layout.operator("hops.edit_bool_knife", text="Knife", icon_value=get_icon_id("Knife"))
            layout.operator("hops.edit_bool_intersect", text="Intersection", icon_value=get_icon_id("Intersection"))

class HOPS_MT_ModSubmenu(bpy.types.Menu):
    bl_label = 'Mod Submenu'
    bl_idname = 'HOPS_MT_ModSubmenu'

    def draw(self, context):
        layout = self.layout

        object = context.active_object

        if object.mode == "OBJECT" and object.type == "MESH":
            layout.operator_context = 'INVOKE_DEFAULT'

            layout.operator("hops.adjust_bevel", text="Bevel", icon="MOD_BEVEL")
            layout.operator("hops.adjust_tthick", text="Solidify", icon="MOD_SOLIDIFY")
            layout.operator("hops.adjust_array", text="Array", icon="MOD_ARRAY")
            layout.operator("hops.mirror_gizmo", text="Mirror", icon="MOD_MIRROR")
            layout.separator()
            layout.operator("hops.mod_screw", text="Screw", icon="MOD_SCREW")
            if (2, 82, 4) < bpy.app.version:
                layout.operator("hops.mod_weld", text="Weld", icon="AUTOMERGE_OFF")
            layout.operator("hops.mod_displace", text="Displace", icon="MOD_DISPLACE")
            layout.operator("hops.mod_decimate", text="Decimate", icon="MOD_DECIM")
            layout.operator("hops.mod_triangulate", text="Triangulate", icon="MOD_TRIANGULATE")
            layout.operator("hops.mod_smooth", text="Smooth", icon="MOD_SMOOTH")
            layout.operator("hops.mod_lsmooth", text="Laplacian Smooth", icon="MOD_SMOOTH")
            layout.operator("hops.mod_weighted_normal", text="Weighted Normal", icon="MOD_NORMALEDIT")
            layout.separator()
            layout.operator("hops.mod_wireframe", text="Wireframe", icon="MOD_WIREFRAME")
            layout.operator("hops.mod_simple_deform", text="Simple Deform", icon="MOD_SIMPLEDEFORM")
            layout.operator("hops.mod_subdivision", text="Subdivision", icon="MOD_SUBSURF")
            layout.operator("hops.mod_lattice", text="Lattice", icon="MOD_LATTICE")
            layout.operator("hops.mod_cast", text="Cast", icon="MOD_CAST")
            layout.operator("hops.mod_skin", text="Skin", icon="MOD_SKIN")
            layout.operator("hops.mod_shrinkwrap", text="Shrinkwrap", icon="MOD_SHRINKWRAP")
            layout.separator()
            #layout.operator("hops.2d_bevel", text="2d Bevel", icon="MOD_BEVEL")
            #layout.menu("HOPS_MT_Tool_array", text="Circular Array Axis", icon_value=get_icon_id("ArrayCircle"))
            #layout.operator("hops.radial_array", text="Radial Array", icon_value=get_icon_id("ArrayCircle"))
            layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")
            layout.operator("hops.bool_toggle_viewport", text= "Toggle Modifiers", icon_value=get_icon_id("Tris")).all_modifiers = False
            layout.separator()
            layout.operator("hops.mod_apply", text="Apply Modifiers", icon="REC")

        if object.mode == "EDIT" and object.type == "MESH":
            layout.operator_context = 'INVOKE_DEFAULT'

            layout.operator("hops.adjust_bevel", text="Bevel", icon="MOD_BEVEL")
            if (2, 82, 4) < bpy.app.version:
                layout.operator("hops.mod_weld", text="Weld", icon="AUTOMERGE_OFF")
            layout.operator("hops.mod_lattice", text="Lattice", icon="MOD_LATTICE")
            layout.operator("hops.mod_hook", text="Hook", icon="HOOK")
            layout.operator("hops.mod_mask", text="Mask", icon="MOD_MASK")
            if (2, 82, 4) < bpy.app.version:
                layout.operator("hops.mod_weld", text="Weld", icon="AUTOMERGE_OFF")


class HOPS_MT_ST3MeshToolsSubmenu(bpy.types.Menu):
    bl_label = 'ST3 Mesh Tools Submenu'
    bl_idname = 'HOPS_MT_ST3MeshToolsSubmenu'

    def draw(self, context):
        layout = self.layout

        object = context.active_object

        if object.mode == "EDIT" and object.type == "MESH":
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("hops.curve_extrude", text="Curve Extrude", icon="CURVE_DATA")
            layout.operator("hops.flatten_to_face", text="Flatten to Face", icon="FACESEL")
            layout.operator("hops.mesh_align", text="Align to Face", icon="MOD_EXPLODE")
            layout.operator("hops.selection_to_boolean", text="Selection to Boolean", icon="MOD_BOOLEAN")
            layout.separator()
