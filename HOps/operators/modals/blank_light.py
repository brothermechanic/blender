import bpy
import math
import random
from gpu_extras.batch import batch_for_shader
from math import cos, sin, pi, radians, degrees
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix, Vector, geometry, Quaternion
from ... ui_framework.master import Master
from ... preferences import get_preferences
from ... graphics.drawing2d import draw_text
from ... addon.utility import method_handler
from ... ui_framework.utils.mods_list import get_mods_list
from ... utility.base_modal_controls import Base_Modal_Controls


class HOPS_OT_Blank_Light(bpy.types.Operator):

    """Blank Light Rig"""
    bl_idname = "hops.blank_light"
    bl_label = "Blank Light"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """LMB - Blank Light Rig Creator
Creates a randomized light rig 

Press H for help"""
    """"""


    def invoke(self, context, event):

        # Props
        self.master = None
        self.base_controls = None
        self.empty = None
        self.lights = []

        # Setup
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.base_controls = Base_Modal_Controls(context=context, event=event)
        self.empty = get_light_empty(context)
        self.lights = get_lights(self.empty)
        if self.lights == []:
            self.lights = randomize_all_lights(context, self.empty, self.lights)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context=context, event=event)

        # Navigation
        if self.base_controls.pass_through:
            if not self.master.is_mouse_over_ui():
                return {'PASS_THROUGH'}

        # Confirm
        elif event.type == 'LEFTMOUSE':
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                return {'FINISHED'}

        # Cancel
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if not self.master.is_mouse_over_ui():
                self.master.run_fade()
                return {'CANCELLED'}

        # Randomize
        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.value == 'PRESS':
            self.lights = randomize_all_lights(context, self.empty, self.lights)

        # Set all colors to white
        elif event.type == 'W' and event.value == 'PRESS':
            set_all_colors_to_white(self.lights)

        # Increase light energy
        elif event.type in self.base_controls.keyboard_increment:
            if event.value == 'PRESS':
                adjust_light_energy(self.lights, increase=True)

        # Decrease light energy
        elif event.type in self.base_controls.keyboard_decrement:
            if event.value == 'PRESS':
                adjust_light_energy(self.lights, increase=False)

        # Desaturate colors
        elif event.type == 'D' and event.value == 'PRESS':
            desaturate_light_colors(self.lights)

        # Saturate colors
        elif event.type == 'S' and event.value == 'PRESS':
            saturate_light_colors(self.lights)

        # Randomize colors
        elif event.type == 'C' and event.value == 'PRESS':
            randomize_light_colors(self.lights)

        # Shading
        elif event.type == 'TAB' and event.value == 'PRESS':
            types = ['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']
            index = types.index(context.space_data.shading.type)
            context.space_data.shading.type = types[(index + 1) % len(types)]

        self.draw_ui(context=context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def draw_ui(self, context):

        self.master.setup()

        #--- Fast UI ---#
        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            point_lights = 0
            area_lights = 0
            sun_lights = 0

            for light in self.lights:
                if light.data.type == 'POINT':
                    point_lights += 1
                elif light.data.type == 'AREA':
                    area_lights += 1
                elif light.data.type == 'SUN':
                    sun_lights += 1

            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(f'P : {point_lights}')
                win_list.append(f'A : {area_lights}')
                win_list.append(f'S : {sun_lights}')
            else:
                win_list.append(f'Point Lights: {point_lights}')
                win_list.append(f'Area Lights: {area_lights}')
                win_list.append(f'Sun Lights: {sun_lights}')
            

            # Help
            help_list.append(["W",   "Set all lights to White"])
            help_list.append(["+ -", "Adjust energy"])
            help_list.append(["D",   "Desaturate Colors"])
            help_list.append(["S",   "Saturate Colors"])
            help_list.append(["C",   "Randomize light colors"])
            help_list.append(["M",   "Toggle lights list"])
            help_list.append(["H",   "Toggle help"])
            help_list.append(["~",   "Toggle Viewport Display"])

            # Mods
            for light in self.lights:
                mods_list.append([light.name, ""])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ArrayCircle", mods_list=mods_list, active_mod_name=active_mod)

        self.master.finished()


####################################################
#   HIGH LEVEL FUNCTIONS
####################################################

def get_light_empty(context: bpy.context):
    '''Get the light collection or return the exsisting one.'''

    empty_name = "HOPS Light Empty"
    empty = None
    collection = context.collection

    # Check if the empty exsist
    for obj in collection.objects:
        if obj.name[:16] == empty_name:
            empty = obj
            break
    
    # If no empty was in the collection make a new empty
    if empty == None:
        empty = bpy.data.objects.new(empty_name, None )
        context.collection.objects.link(empty)
        empty.empty_display_size = .5
        empty.empty_display_type = 'SPHERE'

    return empty


def get_lights(empty):
    '''Get all the light objects on parent object.'''

    lights = []

    for obj in empty.children:
        if obj.type == 'LIGHT':
            lights.append(obj)

    return lights


def randomize_all_lights(context, empty, lights):
    '''Delete all the lights and rebuild everything randomly.'''

    for light in lights:
        bpy.data.objects.remove(light)
    
    lights = []

    # Add random point lights
    point_lights = add_random_point_lights(context, empty)
    lights = lights + point_lights

    # Add random sun lights
    sun_lights = add_random_sun_lights(context, empty)
    lights = lights + sun_lights

    # Add random area lights
    area_lights = add_random_area_lights(context, empty)
    lights = lights + area_lights

    return lights


def add_random_point_lights(context, empty):
    '''Create point lights.'''

    lights = []

    light_count = random.randint(0, 6)
    radius = random.uniform(10, 30)
    
    # Place in circle
    for i in range(light_count):
        
        # Sweep angle
        angle = i * math.pi * 2 / light_count
        angle += random.uniform(-.5, .5)

        # Location
        x_loc = cos(angle) * radius
        y_loc = sin(angle) * radius
        z_loc = random.uniform(2, 6)
        location = (x_loc, y_loc, z_loc)

        # Create light
        new_light = add_light(context, empty, location=location, light_type='POINT')

        # Color
        set_random_light_color(new_light)

        # Energy
        new_light.data.energy = random.uniform(50, 1000)

        # Store
        lights.append(new_light)

    return lights


def add_random_sun_lights(context, empty):
    '''Create sun lights.'''

    lights = []

    light_count = random.randint(0, 3)
    radius = random.uniform(15, 20)
    
    # Place in circle
    for i in range(light_count):
        
        # Sweep angle
        angle = i * math.pi * 2 / light_count
        angle += random.uniform(-.5, .5)

        # Location
        x_loc = cos(angle) * radius
        y_loc = sin(angle) * radius
        z_loc = random.uniform(-5, 20)
        location = (x_loc, y_loc, z_loc)

        # Create light
        new_light = add_light(context, empty, location=location, light_type='SUN')

        # Color
        set_random_light_color(new_light)

        # Energy
        new_light.data.energy = random.uniform(1, 5)

        # Rotation
        up_vec = Vector((0, 0, 1))
        euler_rot = up_vec.rotation_difference(location).to_euler()
        new_light.rotation_euler = euler_rot

        # Store
        lights.append(new_light)

    return lights


def add_random_area_lights(context, empty):
    '''Create sun lights.'''

    lights = []

    light_count = random.randint(1, 4)
    radius = random.uniform(15, 20)
    
    # Place in circle
    for i in range(light_count):
        
        # Sweep angle
        angle = i * math.pi * 2 / light_count
        angle += random.uniform(-.5, .5)

        # Location
        x_loc = cos(angle) * radius
        y_loc = sin(angle) * radius
        z_loc = random.uniform(-5, 20)
        location = (x_loc, y_loc, z_loc)

        # Create light
        new_light = add_light(context, empty, location=location, light_type='AREA')

        # Color
        set_random_light_color(new_light)

        # Energy
        new_light.data.energy = random.uniform(50, 7000)

        # Size
        new_light.data.size = random.uniform(1, 10)

        # Rotation
        up_vec = Vector((0, 0, 1))
        euler_rot = up_vec.rotation_difference(location).to_euler()
        new_light.rotation_euler = euler_rot

        # Store
        lights.append(new_light)

    return lights


####################################################
#   LOWER LEVEL FUNCTIONS
####################################################


def add_light(context, empty, location=(0,0,0), look_target=(0,0,0), light_type='POINT'):
    '''Create a new light, return light ID.'''

    light_data = bpy.data.lights.new(name='HOPS_Light_Data', type=light_type)
    light_obj = bpy.data.objects.new(f'HOPS_LIGHT_{light_type}', object_data=light_data)
    light_obj.location = location
    light_obj.data.use_contact_shadow = True
    context.collection.objects.link(light_obj)
    light_obj.parent = empty

    return light_obj


def set_random_light_color(light):
    '''Set light color.'''

    r = random.uniform(0, 1)
    g = random.uniform(0, 1)
    b = random.uniform(0, 1)
    light.data.color = (r, g, b)


def set_all_colors_to_white(lights):
    '''Sets all the color values to white.'''

    for light in lights:
        light.data.color = (1, 1, 1)


def adjust_light_energy(lights, increase=True):
    '''Increase the energy of each light based on increase.'''

    for light in lights:

        if light.data.type == 'POINT':
            value = 100 if increase else -(light.data.energy / 15)
            light.data.energy += value

        elif light.data.type == 'AREA':
            value = 100 if increase else -(light.data.energy / 15)
            light.data.energy += value

        elif light.data.type == 'SUN':
            value = .25 if increase else -(light.data.energy / 15)
            light.data.energy += value

        if light.data.energy < 0:
            light.data.energy = 0


def desaturate_light_colors(lights):
    '''Desaturate the light colors by moving values to white.'''

    for light in lights:
        for index, value in enumerate(light.data.color):
            diff = 1 - value
            if diff > 0:
                light.data.color[index] += diff / 10


def saturate_light_colors(lights):
    '''Saturate the light colors by moving values to its closer side.'''

    for light in lights:
        if light.data.color.s < 1:
            diff = 1 - light.data.color.s
            light.data.color.s += diff / 10


def randomize_light_colors(lights):
    '''Randomize the light colors.'''

    for light in lights:
        set_random_light_color(light)









