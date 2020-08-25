import bpy
import textwrap

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty

from ... utility import names, screen


def draw(preference, context, layout):

    write_text(layout, info_text, width=bpy.context.region.width / screen.dpi_factor() / 8)


def write_text(layout, text, width = 30, icon = "NONE"):
    col = layout.column(align = True)
    col.scale_y = 0.85
    prefix = " "
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            col.label(text=prefix + line, icon = icon)
            if icon != "NONE": prefix = "     "
            icon = "NONE"


info_text = """HardOps is a toolset to maximize hard surface efficiency. This tool began back in
2015 and still continues. Thanks to everyone's continued support and usage the tool continues to live.
We hope you enjoy using HardOps.
""".replace("\n", " ")
