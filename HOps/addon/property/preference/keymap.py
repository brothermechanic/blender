import bpy
import textwrap

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, EnumProperty
from ... utility import names, addon

import rna_keymap_ui


def get_hotkey_entry_item(km, kmi_name, kmi_value, properties):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if properties == 'name':
                if km.keymap_items[i].properties.name == kmi_value:
                    return km_item
            elif properties == 'tab':
                if km.keymap_items[i].properties.tab == kmi_value:
                    return km_item
            elif properties == 'none':
                return km_item
    return None


sharp_modes = [
    ("SSHARP", "Ssharp", ""),
    ("CSHARP", "Csharp", ""),
    ("RESHARP", "Resharp", ""),
    ("CSHARPBEVEL", "CsharpBevel", ""),
    ("SSHARPWN", "Weighted Mod", ""),
    ("AUTOSMOOVE", "Autosmooth", ""),
    ("CLEANSHARP", "Cleansharp", "")]


class hops(PropertyGroup):

    sharp: EnumProperty(
        name="Sharp Modes",
        default='SSHARP',
        items=sharp_modes)

    sharp_alt: EnumProperty(
        name="Sharp Modes",
        default='SSHARPWN',
        items=sharp_modes)

    sharp_ctrl: EnumProperty(
        name="Sharp Modes",
        default='CSHARP',
        items=sharp_modes)

    sharp_shift: EnumProperty(
        name="Sharp Modes",
        default='AUTOSMOOVE',
        items=sharp_modes)

    sharp_alt_ctrl: EnumProperty(
        name="Sharp Modes",
        default='SSHARP',
        items=sharp_modes)

    sharp_shift_ctrl: EnumProperty(
        name="Sharp Modes",
        default='RESHARP',
        items=sharp_modes)

    sharp_alt_shift: EnumProperty(
        name="Sharp Modes",
        default='SSHARP',
        items=sharp_modes)

    expand_sharpen: BoolProperty(name="expand sharpen options", default=False)


def header_row(row, prop, label='', emboss=False):
    preference = addon.preference()
    icon = 'DISCLOSURE_TRI_RIGHT' if not getattr(preference.keymap, prop) else 'DISCLOSURE_TRI_DOWN'
    row.alignment = 'LEFT'
    row.prop(preference.keymap, prop, text='', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.25
    sub.prop(preference.keymap, prop, text='', icon=icon, emboss=emboss)
    row.prop(preference.keymap, prop, text=F'{label}', emboss=emboss)

    sub = row.row(align=True)
    sub.scale_x = 0.75
    sub.prop(preference.keymap, prop, text=' ', icon='BLANK1', emboss=emboss)


def draw(preference, context, layout):

    box = layout.box()
    split = box.split()
    col = split.column()

    # col(preference.property, 'hops_modal_help', layout.row(), label='Show Help For modal Operators')

    col.separator()
    header_row(col.row(align=True), 'expand_sharpen', label='Sharpen keymap')
    if preference.keymap.expand_sharpen:
        col.separator()
        col.label(text='Sharpen Activation Hotkeys')
        col.separator()
        col.prop(preference.keymap, "sharp", text="Main")
        col.prop(preference.keymap, "sharp_alt", text="ALt")
        col.prop(preference.keymap, "sharp_ctrl", text="Ctrl")
        col.prop(preference.keymap, "sharp_shift", text="Shift")
        col.prop(preference.keymap, "sharp_alt_shift", text="Alt + Shift")
        col.prop(preference.keymap, "sharp_alt_ctrl", text="Alt + Ctrl")
        col.prop(preference.keymap, "sharp_shift_ctrl", text="Shift + Ctrl")
        col.separator()
        col.separator()
        col.separator()
        col.label(text='Do not remove hotkeys, disable them instead.')
        col.separator()
        col.label(text='Hotkeys')

    col.separator()

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    col.label(text='menus:')

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'wm.call_menu_pie', 'HOPS_MT_MainPie', 'name')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'HOPS_MT_MainMenu', 'name')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'hops.helper', 'none', 'none')
    # kmi = get_hotkey_entry_item(km, 'hops.helper', 'MODIFIERS', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'hops.bev_multi', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'HOPS_MT_MaterialListMenu', 'name')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'HOPS_MT_ViewportSubmenu', 'name')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    col.label(text='operators:')

    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'hops.mirror_gizmo', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    col.label(text='booleans:')
    col.separator()
    km = kc.keymaps['Object Mode']
    kmi = get_hotkey_entry_item(km, 'hops.bool_union_hotkey', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['Object Mode']
    kmi = get_hotkey_entry_item(km, 'hops.bool_difference_hotkey', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['Object Mode']
    kmi = get_hotkey_entry_item(km, 'hops.slash_hotkey', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['Object Mode']
    kmi = get_hotkey_entry_item(km, 'hops.bool_inset', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.label(text='edit mode:')

    col.separator()
    km = kc.keymaps['Mesh']
    kmi = get_hotkey_entry_item(km, 'hops.edit_bool_union', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.separator()
    km = kc.keymaps['Mesh']
    kmi = get_hotkey_entry_item(km, 'hops.edit_bool_difference', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")

    col.label(text='3rd Party:')

    col.separator()
    col.label(text='External Support:')
    if addon_exists('mira_tools'):
        col.separator()
        km = kc.keymaps['Mesh']
        kmi = get_hotkey_entry_item(km, 'mesh.curve_stretch', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")
    else:
        col.label(text="nothing to see here")

    col.separator()
    col.label(text='Extended:')
    col.separator()
    km = kc.keymaps['3D View']
    kmi = get_hotkey_entry_item(km, 'hops.tilde_remap', 'none', 'none')
    if kmi:
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        col.label(text="No hotkey entry found")
        col.label(text="restore hotkeys from interface tab")



def addon_exists(name):
    for addon_name in bpy.context.preferences.addons.keys():
        if name in addon_name: return True
    return False
