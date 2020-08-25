import bpy, bmesh, gpu, bgl, math
from gpu_extras.batch import batch_for_shader
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... preferences import get_preferences
from ... utility import modifier
from ... utility.base_modal_controls import Base_Modal_Controls
from ...ui_framework.master import Master
from ...ui_framework.utils.mods_list import get_mods_list


class HOPS_OT_RadialArray(bpy.types.Operator):
    bl_idname = "hops.radial_array"
    bl_label = "Radial Array"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING', 'GRAB_CURSOR'}
    bl_description = """LMB - Array around object center
Ctrl + LMB - Array around 3D cursor"""

    direction: bpy.props.EnumProperty(
        name="Direction",
        description="What axis to displace on",
        items=[
            ('X', "X", "Displace on the X axis"),
            ('Y', "Y", "Displace on the Y axis"),
            ('Z', "Z", "Displace on the Z axis")],
        default='Y')

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="What axis to array around",
        items=[
            ('X', "X", "Array around the X axis"),
            ('Y', "Y", "Array around the Y axis"),
            ('Z', "Z", "Array around the Z axis")],
        default='Z')

    segments: bpy.props.IntProperty(
        name="Segments",
        description="How many copies to make",
        default=8,
        min=1)

    rotation: bpy.props.IntProperty(
        name="Rotation",
        description="Amount of rotation",
        default=360,
        min=15)

    displace: bpy.props.FloatProperty(
        name="Displace",
        description="How far in or out to displace",
        default=0)

    cursor: bpy.props.BoolProperty(
        name="3D Cursor",
        description="Use the 3D cursor as origin",
        default=False)

    def __init__(self):

        # Modal UI
        self.master = None


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'


    def draw(self, context):
        self.layout.label(text=f"Direction: {self.direction}")
        self.layout.label(text=f"Axis: {self.axis}")
        self.layout.label(text=f"Segments: {self.segments}")
        self.layout.label(text=f"Displace: {self.displace:.3f}")
        self.layout.label(text=f"Origin: {'3D Cursor' if self.cursor else 'Object Center'}")


    def execute(self, context):
        return {'FINISHED'}


    def invoke(self, context, event):

        self.base_controls = Base_Modal_Controls(context, event)

        # Set internal variables
        self.modal_scale = get_preferences().ui.Hops_modal_scale
        self.obj = context.active_object
        self.index = 0

        # Set internal variables
        self.empty = None
        self.displace_mod = None
        self.array_mod = None

        # Find empty and modifiers
        for a, b in zip(self.obj.modifiers[:-1], self.obj.modifiers[1:]):
            if a.type == 'DISPLACE' and b.type == 'ARRAY' and b.use_object_offset == True:
                self.empty = b.offset_object
                self.displace_mod = a
                self.array_mod = b
                break

        # Set internal variables
        self.empty_new = not self.empty
        self.displace_new = not self.displace_mod
        self.array_new = not self.array_mod

        # Create empty and modifiers
        if self.empty_new:
            self.empty = bpy.data.objects.new("Radial Empty", None)
            self.empty.empty_display_type = 'SPHERE'
            self.empty.parent = self.obj
            for col in self.obj.users_collection:
                if col not in self.empty.users_collection:
                    col.objects.link(self.empty)

        if self.displace_new:
            self.displace_mod = self.obj.modifiers.new("Radial Displace", 'DISPLACE')
            self.displace_mod.show_expanded = False

            self.displace_mod.show_render = get_preferences().property.Hops_twist_radial_sort
            self.displace_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort

            self.displace_mod.mid_level = 0.0
            self.displace_mod.direction = self.direction
            self.displace_mod.strength = self.displace

        if self.array_new:
            self.array_mod = self.obj.modifiers.new("Radial Array", 'ARRAY')
            self.array_mod.show_expanded = False
            
            self.array_mod.show_render = get_preferences().property.Hops_twist_radial_sort
            self.array_mod.show_in_editmode = not get_preferences().property.Hops_twist_radial_sort

            self.array_mod.use_constant_offset = False
            self.array_mod.use_relative_offset = False
            self.array_mod.use_object_offset = True
            self.array_mod.offset_object = self.empty
            self.array_mod.count = self.segments

        # Set internal variables
        self.direction = self.displace_mod.direction
        self.axis = "YZX"["XYZ".find(self.direction)]
        self.segments = self.segments_buffer = self.array_mod.count
        self.displace = self.displace_buffer = self.displace_mod.strength

        # Try to find the axis from the empty's drivers
        if self.empty.animation_data:
            for fcurve in self.empty.animation_data.drivers:
                if fcurve.data_path == "rotation_euler":
                    self.axis = "XYZ"[fcurve.array_index]

        # Store modifier settings
        self.displace_settings = {}
        self.displace_settings["show_viewport"] = self.displace_mod.show_viewport
        self.displace_settings["mid_level"] = self.displace_mod.mid_level
        self.displace_settings["direction"] = self.displace_mod.direction
        self.displace_settings["strength"] = self.displace_mod.strength

        self.array_settings = {}
        self.array_settings["use_constant_offset"] = self.array_mod.use_constant_offset
        self.array_settings["use_relative_offset"] = self.array_mod.use_relative_offset
        self.array_settings["use_object_offset"] = self.array_mod.use_object_offset
        self.array_settings["offset_object"] = self.array_mod.offset_object
        self.array_settings["count"] = self.array_mod.count

        # Configure existing modifiers
        if not self.displace_new:
            self.displace_mod.mid_level = 0.0
            self.displace_mod.direction = self.direction
            self.displace_mod.strength = self.displace

        if not self.array_new:
            self.array_mod.use_constant_offset = False
            self.array_mod.use_relative_offset = False
            self.array_mod.use_object_offset = True
            self.array_mod.offset_object = self.empty
            self.array_mod.count = self.segments

        # Move object origin
        self.location = self.obj.location[:]
        self.cursor_prev = bool(self.cursor)
        self.cursor = event.ctrl and event.type == 'LEFTMOUSE'

        if self.empty_new:
            self.set_origin(context)
        else:
            self.cursor = self.origin_outside_bounds(context)

        # Create driver
        self.direction_prev = str(self.direction)
        self.axis_prev = str(self.axis)
        self.create_driver(context, self.rotation)

        # Set internal variables
        self.adjusting = 'NONE' if self.cursor else 'DISPLACE'
        self.displace_center = float(self.displace)
        self.displace_cursor = float(self.displace)
        self.set_displace(context)

        #UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


    def modal(self, context, event):

        self.master.receive_event(event=event)
        self.base_controls.update(context, event)

        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif self.base_controls.confirm:
            self.confirm(context)
            self.report({'INFO'}, "Finished")
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            return {'FINISHED'}

        elif self.base_controls.cancel:
            self.cancel(context)
            self.report({'INFO'}, "Cancelled")
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            return {'CANCELLED'}

        elif event.type == 'A' and event.value == 'PRESS':
            self.displace_mod.show_viewport = not self.displace_mod.show_viewport
            self.report({'INFO'}, f"{'Enabled' if self.displace_mod.show_viewport else 'Disabled'} Displacement")

        elif event.type == 'S' and event.value == 'PRESS':
            self.adjusting = 'NONE' if self.adjusting == 'SEGMENTS' else 'SEGMENTS'
            self.report({'INFO'}, f"{'Started' if self.adjusting == 'SEGMENTS' else 'Stopped'} Adjusting Segments")

        elif event.type == 'D' and event.value == 'PRESS':
            self.adjusting = 'NONE' if self.adjusting == 'DISPLACE' else 'DISPLACE'
            self.report({'INFO'}, f"{'Started' if self.adjusting == 'DISPLACE' else 'Stopped'} Adjusting Displace")

        elif event.type == 'Z' and event.value == 'PRESS':
            self.direction = "YZX"["XYZ".find(self.direction)]
            self.displace_mod.direction = self.direction
            self.report({'INFO'}, f"Displace Axis: {self.direction}")

        elif event.type == 'X' and event.value == 'PRESS':
            self.direction = "YZX"["XYZ".find(self.direction)]
            self.displace_mod.direction = self.direction
            self.axis = "YZX"["XYZ".find(self.axis)]
            self.create_driver(context, self.rotation)
            self.report({'INFO'}, f"Rotate Axis: {self.axis}")


        elif event.type == 'R' and event.value == 'PRESS':
            rotations = ['360', '180', '90', '60', '45', '30', '15']
            self.index += 1
            if self.index + 1 == len(rotations):
                self.index = 0
            self.rotation = int(rotations[self.index])
            self.report({'INFO'}, F'Rotation : {self.rotation}')

        elif event.type == 'C' and event.value == 'PRESS':
            self.adjusting = 'NONE'
            self.cursor = not self.cursor
            self.set_displace(context)
            self.set_origin(context)
            self.create_driver(context, self.rotation)
            self.report({'INFO'}, f"Origin: {'3D Cursor' if self.cursor else 'Object Center'}")

        elif self.base_controls.scroll:
            self.segments_buffer += self.base_controls.scroll
            self.segments_buffer = max(self.segments_buffer, 1)
            self.segments = round(self.segments_buffer)
            self.array_mod.count = self.segments
            self.report({'INFO'}, f"Segments: {self.segments}")

        elif event.type == 'MOUSEMOVE' and self.adjusting == 'SEGMENTS':
            offset = self.base_controls.mouse
            self.segments_buffer += offset
            self.segments_buffer = max(self.segments_buffer, 1)
            self.segments = round(self.segments_buffer)
            self.array_mod.count = self.segments

        elif event.type == 'MOUSEMOVE' and self.adjusting == 'DISPLACE':
            offset = self.base_controls.mouse * 2.5
            self.displace_buffer -= offset
            digits = 2 if event.ctrl and event.shift else 1 if event.ctrl else 3
            self.displace = round(self.displace_buffer, digits)
            self.displace_mod.strength = self.displace

        elif self.base_controls.tilde and event.shift == True:
            bpy.context.space_data.overlay.show_overlays = not bpy.context.space_data.overlay.show_overlays

        self.create_driver(context, self.rotation)


        self.draw_master(context=context)

        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


    def set_displace(self, context):
        if self.cursor:
            self.displace_center = float(self.displace)
            self.displace_buffer = self.displace_cursor
            self.displace = self.displace_cursor
            self.displace_mod.strength = self.displace_cursor

        else:
            self.displace_cursor = float(self.displace)
            self.displace_buffer = self.displace_center
            self.displace = self.displace_center
            self.displace_mod.strength = self.displace_center


    def set_origin(self, context):
        self.empty.parent = None
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR' if self.cursor else 'ORIGIN_GEOMETRY', center='BOUNDS')
        self.empty.parent = self.obj
        self.empty.location = (0,0,0)
        self.empty.rotation_euler = (0,0,0)
        self.empty.scale = (1,1,1)


    def origin_outside_bounds(self, context):
        temp = bpy.data.objects.new("Bounding Box", self.obj.data)
        bb = temp.bound_box[:]
        bpy.data.objects.remove(temp)
        x = bb[6][0] < 0 or bb[0][0] > 0
        y = bb[6][1] < 0 or bb[0][1] > 0
        z = bb[6][2] < 0 or bb[0][2] > 0
        return x or y or z


    def create_driver(self, context, rotation):
        [self.empty.driver_remove("rotation_euler", i) for i in range(3)]
        self.empty.rotation_euler = (0,0,0)
        index = "XYZ".find(self.axis)
        self.driver = self.empty.driver_add("rotation_euler", index).driver
        count = self.driver.variables.new()
        count.name = "count"
        count.targets[0].id = self.obj
        count.targets[0].data_path = f"modifiers[\"{self.array_mod.name}\"].count"
        self.driver.expression = f"{math.radians(self.rotation)} / count"



    def confirm(self, context):
        modifier.sort(self.obj, sort_types=['WEIGHTED_NORMAL'])

        if get_preferences().property.workflow == 'DESTRUCTIVE':
            modifier.apply(self.displace_mod)
            modifier.apply(self.array_mod)
            bpy.data.objects.remove(self.empty)


    def cancel(self, context):
        self.direction = self.direction_prev
        self.axis = self.axis_prev

        self.empty.parent = None
        cursor = context.scene.cursor.location[:]
        context.scene.cursor.location = self.location[:]
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
        context.scene.cursor.location = cursor[:]
        self.empty.parent = self.obj
        self.empty.location = (0,0,0)
        self.empty.rotation_euler = (0,0,0)
        self.empty.scale = (1,1,1)

        if self.displace_new:
            self.obj.modifiers.remove(self.displace_mod)
        else:
            self.displace_mod.show_viewport = self.displace_settings["show_viewport"]
            self.displace_mod.mid_level = self.displace_settings["mid_level"]
            self.displace_mod.direction = self.displace_settings["direction"]
            self.displace_mod.strength = self.displace_settings["strength"]

        if self.array_new:
            self.obj.modifiers.remove(self.array_mod)
        else:
            self.array_mod.use_constant_offset = self.array_settings["use_constant_offset"]
            self.array_mod.use_relative_offset = self.array_settings["use_relative_offset"]
            self.array_mod.use_object_offset = self.array_settings["use_object_offset"]
            self.array_mod.offset_object = self.array_settings["offset_object"]
            self.array_mod.count = self.array_settings["count"]

        if self.empty_new:
            bpy.data.objects.remove(self.empty)
        else:
            self.create_driver(context, self.rotation)


    def draw_master(self, context):

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################


        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []
            mods_list = []
            active_mod = ""

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1: #Fast Floating
                win_list.append(f"{self.axis}")
                win_list.append(f"{self.segments}")
                win_list.append(f"{self.displace:.2f}")
            else:
                win_list.append("Radial Array")
                win_list.append(f"{self.axis}")
                win_list.append(f"{self.segments}")
                win_list.append(f"{self.displace:.3f}")

            # Help
            help_list.append(["Scroll", "Increment Segments"])
            help_list.append(["A",      "Toggle Displace"])
            help_list.append(["S",      "Adjust Segments"])
            help_list.append(["D",      "Adjust Displace"])
            help_list.append(["Z",      "Increment Displace Axis"])
            help_list.append(["R",      "Change radial to 180/90/45/30"])
            help_list.append(["X",      "Increment Rotate Axis"])
            help_list.append(["C",      "Array Around 3D Cursor / Object Center"])
            help_list.append(["M",      "Toggle mods list."])
            help_list.append(["H",      "Toggle help."])
            help_list.append(["~",      "Toggle viewport displays."])

            # Mods
            if self.displace_mod != None:
                active_mod = self.displace_mod.name

            mods_list = get_mods_list(mods=bpy.context.active_object.modifiers)

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ArrayCircle", mods_list=mods_list, active_mod_name=active_mod)

        # Finished
        self.master.finished()
