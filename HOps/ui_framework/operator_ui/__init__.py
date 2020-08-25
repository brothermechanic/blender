import bpy
import gpu
import math
import time
import mathutils
from bgl import *
from mathutils import Vector
from math import cos, sin, pi, radians, degrees
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from bpy.props import IntProperty, FloatProperty

from ..graphics.draw import render_text, render_quad, draw_border_lines
from ..utils.geo import get_blf_text_dims

from ...preferences import get_preferences
from ...addon.utility import method_handler
from ...utils.blender_ui import get_dpi, get_dpi_factor


class Data():
    '''Global communications from operator to ui modal.'''
    # Fade Variables
    start_time = 0
    time_difference = 0
    hold_complete = False

    # Transitions
    active_count = 0

    # Display Data
    draw_data = []

    draw_bg = False
    draw_border = False


class Master():
    '''Used from the modal to launch the drawing.'''


    def receive_draw_data(self, draw_data=[]):

        Data.draw_data = draw_data


    def draw(self, draw_bg=False, draw_border=False):

        prefs = get_preferences()

        if prefs.ui.Hops_operator_display:

            Data.draw_bg = draw_bg
            Data.draw_border = draw_border

            Data.active_count += 1
            bpy.ops.hops.ui_draw('INVOKE_DEFAULT')


class HOPS_OT_UI_Draw(bpy.types.Operator):
    '''UI Modal'''

    bl_idname = "hops.ui_draw"
    bl_label = "Drawing for operators"
    bl_options = {"INTERNAL"}


    def __init__(self):

        self.shader = None
        self.timer = None
        self.prefs = get_preferences()


    def invoke(self, context, event):

        # Globals
        Data.start_time = time.time()
        Data.hold_complete = False
        Data.time_difference = 0

        # Fail Safe
        self.start_time = time.time()
        self.max_time = self.prefs.ui.Hops_operator_display_time + self.prefs.ui.Hops_operator_display_time + 3

        #UI System
        self.shader = Shader(context)
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # Fail Safe
        if time.time() - self.start_time > self.max_time:
            self.finished(context)
            return {'FINISHED'}

        # Get the time difference
        Data.time_difference = time.time() - Data.start_time

        # Remove modal if another starts
        if Data.active_count > 1:
            self.finished(context)
            return {'FINISHED'}

        
        # Hold the UI on screen until display time is completed
        if Data.hold_complete == False:

            if Data.time_difference >= self.prefs.ui.Hops_operator_display_time:
                Data.hold_complete = True
                Data.time_difference = 0
                Data.start_time = time.time()

            elif Data.time_difference <= self.prefs.ui.Hops_operator_display_time:

                # Redraw the viewport
                if context.area != None:
                    context.area.tag_redraw()
                return {'PASS_THROUGH'}


        # Fade is finished
        if Data.time_difference > self.prefs.ui.Hops_operator_fade:
            self.finished(context)
            return {'FINISHED'}

        # Redraw the viewport
        if context.area != None:
            context.area.tag_redraw()

        return {'PASS_THROUGH'}

    
    def finished(self, context):
        '''Remove the timer, shader, and reset Data'''

        Data.time_difference = 0
        Data.active_count -= 1

        if self.timer != None:
            context.window_manager.event_timer_remove(self.timer)

        if self.shader != None:
            self.shader.destroy()
            del self.shader

        if context.area != None:
            context.area.tag_redraw()


class Shader():

    def __init__(self, context):

        self.context = context
        self.handle = None

        self.banner = Banner(context=self.context)

        self.setup_handle()

 
    def setup_handle(self):
        '''Setup the draw handle for the UI'''

        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.safe_draw, (self.context, ), "WINDOW", "POST_PIXEL")


    def safe_draw(self, context):
        method_handler(self.draw,
            arguments = (context,),
            identifier = 'UI Framework',
            exit_method = self.destroy)


    def draw(self, context):

        self.banner.draw()


    def destroy(self):

        if self.handle:
            self.handle = bpy.types.SpaceView3D.draw_handler_remove(self.handle, "WINDOW")
            if self.banner:
                del self.banner
            return True

        else:
            return False


class Banner():
    '''Drawing class for operator UI.'''

    def __init__(self, context):

        self.context = context
        self.prefs = get_preferences()
        self.alpha = 1
        self.scale_factor = get_dpi_factor()
        self.setup_colors()

        # Header
        self.header_text_size = 24
        # Body
        self.body_text_size = 14

        # Overall Dims
        self.total_width = 0

        self.prefs_offset = (self.prefs.ui.Hops_operator_ui_offset[0] * self.scale_factor, self.prefs.ui.Hops_operator_ui_offset[1] * self.scale_factor)
        self.left_offset = (self.context.area.width * .5) - (self.total_width * .5) + self.prefs_offset[0]
        self.bottom_offset = 35 * self.scale_factor
        self.text_padding = 10 * self.scale_factor


    def setup_colors(self):

        # Original
        self.prefs_colors = []
        self.prefs_colors.append(self.prefs.color.Hops_UI_text_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_secondary_text_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_text_highlight_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_cell_background_color)
        self.prefs_colors.append(self.prefs.color.Hops_UI_border_color)


    def draw(self):

        if Data.draw_data != []:
            
            self.Hops_UI_text_color            = Vector((self.prefs_colors[0][0], self.prefs_colors[0][1], self.prefs_colors[0][2], self.prefs_colors[0][3]))
            self.Hops_UI_secondary_text_color  = Vector((self.prefs_colors[1][0], self.prefs_colors[1][1], self.prefs_colors[1][2], self.prefs_colors[1][3]))
            self.Hops_UI_text_highlight_color  = Vector((self.prefs_colors[2][0], self.prefs_colors[2][1], self.prefs_colors[2][2], self.prefs_colors[2][3]))
            self.Hops_UI_cell_background_color = Vector((self.prefs_colors[3][0], self.prefs_colors[3][1], self.prefs_colors[3][2], self.prefs_colors[3][3]))
            self.Hops_UI_border_color          = Vector((self.prefs_colors[4][0], self.prefs_colors[4][1], self.prefs_colors[4][2], self.prefs_colors[4][3]))

            # Get total width
            self.get_total_width()

            prefs_offset = (self.prefs.ui.Hops_operator_ui_offset[0] * self.scale_factor, self.prefs.ui.Hops_operator_ui_offset[1] * self.scale_factor)

            # Fade
            if Data.hold_complete == False:
                self.alpha = 1
            else:

                # No fade required
                if self.prefs.ui.Hops_operator_fade == 0:
                    self.alpha = 1

                # Start reducing fade
                else:
                    original_alpha = self.prefs_colors[0][3]
                    alpha = self.Hops_UI_text_color[3] - ((original_alpha / self.prefs.ui.Hops_operator_fade) * Data.time_difference)
                    self.Hops_UI_text_color = Vector((self.prefs_colors[0][0], self.prefs_colors[0][1], self.prefs_colors[0][2], alpha))

                    original_alpha = self.prefs_colors[1][3]
                    alpha = self.Hops_UI_secondary_text_color[3] - ((original_alpha / self.prefs.ui.Hops_operator_fade) * Data.time_difference)
                    self.Hops_UI_secondary_text_color = Vector((self.prefs_colors[1][0], self.prefs_colors[1][1], self.prefs_colors[1][2], alpha))

                    original_alpha = self.prefs_colors[2][3]
                    alpha = self.Hops_UI_text_highlight_color[3] - ((original_alpha / self.prefs.ui.Hops_operator_fade) * Data.time_difference)
                    self.Hops_UI_text_highlight_color  = Vector((self.prefs_colors[2][0], self.prefs_colors[2][1], self.prefs_colors[2][2], alpha))

                    original_alpha = self.prefs_colors[3][3]
                    alpha = self.Hops_UI_cell_background_color[3] - ((original_alpha / self.prefs.ui.Hops_operator_fade) * Data.time_difference)
                    self.Hops_UI_cell_background_color = Vector((self.prefs_colors[3][0], self.prefs_colors[3][1], self.prefs_colors[3][2], alpha))

                    original_alpha = self.prefs_colors[4][3]
                    alpha = self.Hops_UI_border_color[3] - ((original_alpha / self.prefs.ui.Hops_operator_fade) * Data.time_difference)
                    self.Hops_UI_border_color = Vector((self.prefs_colors[4][0], self.prefs_colors[4][1], self.prefs_colors[4][2], alpha))

            self.y_offset = self.prefs_offset[1]

            # Draw header and lines
            if len(Data.draw_data) > 1:
                self.draw_background()
                self.draw_bottom_underline()
                self.draw_body_text()
                self.draw_header_underline()
                self.draw_header_text()

            # Draw only header
            else:
                self.draw_background()
                self.draw_header_text()


    def get_total_width(self):

        # Get the widest text width
        if Data.draw_data != []:

            # Only containts header
            if len(Data.draw_data) == 1:
                self.total_width = get_blf_text_dims(text=str(Data.draw_data[0]), size=self.header_text_size)[0] - (30 * self.scale_factor)

            # Header plus other data
            else:
                longest = ""
                for i in range(len(Data.draw_data)):

                    # Only one item in list
                    if len(Data.draw_data[i]) == 1:
                        if len(Data.draw_data[i][0]) > len(longest):
                            longest = Data.draw_data[i][0]

                    # Two items in list
                    elif len(Data.draw_data[i]) == 2:
                        compare = str(Data.draw_data[i][0]) + str(Data.draw_data[i][1])
                        if len(compare) > len(longest):
                            longest = compare

                self.total_width = get_blf_text_dims(text=str(longest), size=self.body_text_size)[0]
                self.total_width += 150 * self.scale_factor

        self.left_offset = (self.context.area.width * .5) - (self.total_width * .5) + self.prefs_offset[0]


    def draw_background(self):

        # Body height
        height = self.body_text_size *  (len(Data.draw_data) - 1)
        height += self.header_text_size
        if len(Data.draw_data) > 1:
            height += self.text_padding * len(Data.draw_data)

        bottom_padding = 12 * self.scale_factor # This line has to match the line in "draw_bottom_underline()"
        height += bottom_padding

        # Bottom offset
        bottom_offset = self.bottom_offset + self.y_offset

        # Bg padding
        bg_padding = 8 * self.scale_factor

        # Setup for background and border
        top_left     = (self.left_offset -                    bg_padding, bottom_offset + height + bg_padding)
        bottom_left  = (self.left_offset -                    bg_padding, bottom_offset -          bg_padding - bg_padding)
        top_right    = (self.left_offset + self.total_width + bg_padding, bottom_offset + height + bg_padding)
        bottom_right = (self.left_offset + self.total_width + bg_padding, bottom_offset -          bg_padding - bg_padding)

        # Draw background
        if Data.draw_bg:
            render_quad(quad=(
                        top_left, 
                        bottom_left, 
                        top_right, 
                        bottom_right), 
                        color=self.Hops_UI_border_color, 
                        bevel_corners=True)

        # Draw border
        if Data.draw_border:
            vertices = [top_left, bottom_left, top_right, bottom_right]
            draw_border_lines(vertices=vertices, width=get_preferences().ui.Hops_operator_border_size, color=self.Hops_UI_cell_background_color)


    def draw_bottom_underline(self):

        if len(Data.draw_data) > 1:

            bottom_padding = 12 * self.scale_factor

            left_point = (self.left_offset, bottom_padding + self.bottom_offset + self.prefs_offset[1] - (self.text_padding * .5))
            right_point = (self.left_offset + self.total_width, bottom_padding + self.bottom_offset + self.prefs_offset[1] - (self.text_padding * .5))

            self.y_offset += (8 * self.scale_factor) + bottom_padding

            draw_divider_lines(vertices=[left_point, right_point], width=2, color=self.Hops_UI_cell_background_color, bevel_corners=False, format_lines=False)


    def draw_body_text(self):

        if len(Data.draw_data) > 1:

            sample = get_blf_text_dims(text="Sample", size=self.body_text_size)

            # Text items for the body
            for item in Data.draw_data[1:]:

                # Left or Right
                count = 0

                for string in item:
                    
                    if type(string) == float:
                        string = "{0:.3f}".format(string)

                    string = str(string)

                    # Left Side
                    if count == 0:
                        text_dims = get_blf_text_dims(text=string, size=self.body_text_size)
                        pos = (self.left_offset, self.bottom_offset + self.y_offset)

                        render_text(text=string, position=pos, size=self.body_text_size, color=self.Hops_UI_text_color)

                    # Right Side
                    elif count == 1:
                        text_dims = get_blf_text_dims(text=string, size=self.body_text_size)
                        pos = (self.left_offset + self.total_width - text_dims[0], self.bottom_offset + self.y_offset)

                        render_text(text=string, position=pos, size=self.body_text_size, color=self.Hops_UI_secondary_text_color)

                    count += 1

                text_offset = text_dims[1]

                if text_offset <= 0:
                    text_offset = sample[1]

                self.y_offset += text_offset + self.text_padding


    def draw_header_underline(self):

        left_point = (self.left_offset, self.bottom_offset + self.y_offset)
        right_point = (self.left_offset + self.total_width, self.bottom_offset + self.y_offset)

        self.y_offset += 8 * self.scale_factor

        draw_divider_lines(vertices=[left_point, right_point], width=2, color=self.Hops_UI_cell_background_color, bevel_corners=False, format_lines=False)


    def draw_header_text(self):

        string = Data.draw_data[0][0]

        add_height = get_blf_text_dims(text=string, size=self.header_text_size)[1]
        sub_height = get_blf_text_dims(text="XXXXX", size=self.header_text_size)[1]
        additional_height = math.ceil(add_height) - math.ceil(sub_height)

        pos = (self.left_offset, self.bottom_offset + self.y_offset + additional_height)

        render_text(text=string, position=pos, size=self.header_text_size, color=self.Hops_UI_secondary_text_color)


def draw_divider_lines(vertices=[], width=1, color=(0,0,0,1), bevel_corners=True, format_lines=False):
    '''Render quads passed in. \n
        Top Left, Bottom Left, Top Right, Bottom Right
    '''

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glLineWidth(width)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

    glLineWidth(width)
    glDisable(GL_BLEND)

    del shader
    del batch