import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import EnumProperty, PointerProperty

from . import behavior, display, expand, color, info, keymap, links, addons, ui, property
from . operators import operators, mirror
from ... utility import addon

# label row text names


class Hardops(AddonPreferences):
    bl_idname = addon.name

    settings: EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [
            ('UI', 'Ui', ''),
            ('PROPERTY', 'Properties', ''),
            # ('BEHAVIOR', 'Behaviors', ''),
            ('COLOR', 'Color', ''),
            # ('DISPLAY', 'Display', ''),
            ('INFO', 'Info', ''),
            ('KEYMAP', 'Keymap', ''),
            ('LINKS', 'Links/Help', ''),
            ('ADDONS', 'Addons', '')],
        default = 'UI')

    # TODO: add update handler to gizmo toggles that calls gizmo ot

    behavior: PointerProperty(type=behavior.hardflow)
    ui: PointerProperty(type=ui.hops)
    color: PointerProperty(type=color.hops)
    display: PointerProperty(type=display.hardflow)
    expand: PointerProperty(type=expand.hardflow)
    property: PointerProperty(type=property.hops)
    keymap: PointerProperty(type=keymap.hops)

    operator: PointerProperty(type=operators)


    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        box = column.box()
        globals()[self.settings.lower()].draw(self, context, box)


classes = (
    mirror.props,
    operators,
    keymap.hops,
    property.hops,
    behavior.hardflow,
    color.hops,
    ui.hops,
    display.hardflow,
    expand.hardflow,
    Hardops)


def register():
    for cls in classes:
        register_class(cls)
    ui.update_hops_panels(None,None)


def unregister():
    for cls in classes:
        unregister_class(cls)
