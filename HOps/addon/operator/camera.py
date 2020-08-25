import bpy
import math

from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty
from bpy.utils import register_class, unregister_class
from math import radians
from ...ui_framework.operator_ui import Master
from ... preferences import get_preferences

class HOPS_OT_camera_rig(Operator):
    bl_idname = 'hops.camera_rig'
    bl_label = 'Camera Rig'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = '''Set up a turntable camera rig

Ctrl + LMB - Don't make the new camera active in the scene
Shift + LMB - Camera bounce alternative (boomerang)
Ctrl + Shift + LMB - Don't enable passepartout on the new camera'''

    rotations: IntProperty(
        name='Rotations',
        description='How many circles the camera should turn',
        min=1,
        soft_max=15,
        default=2)

    make_active: BoolProperty(
        name='Make Active',
        description='Make the new camera the active one in the scene',
        default=True)

    passepartout: BoolProperty(
        name='Passepartout',
        description='Enable passepartout on the camera',
        default=True)

    bounce: BoolProperty(
        name='Bounce',
        description='Enable bounce camera',
        default=False)

    called_ui = False

    def __init__(self):

        HOPS_OT_camera_rig.called_ui = False

    def invoke(self, context, event):
        self.bounce = event.shift
        self.make_active = not event.ctrl
        if event.ctrl:
            self.passepartout = not event.shift
        return self.execute(context)

    def draw(self, context):
        self.layout.prop(self, 'rotations')
        row = self.layout.row()
        row.prop(self, 'make_active')
        row.prop(self, 'passepartout')
        row.prop(self, 'bounce')

    def execute(self, context):
        # create camera
        data = bpy.data.cameras.new(name='Camera')
        cam = bpy.data.objects.new(name='Camera', object_data=data)
        context.collection.objects.link(cam)

        # make camera active
        if self.make_active:
            context.scene.camera = cam

        # enable passepartout
        if self.passepartout:
            cam.data.passepartout_alpha = 1

        # create empty
        empty = bpy.data.objects.new(name='Empty', object_data=None)
        context.collection.objects.link(empty)

        # create empty driver
        driver = empty.driver_add('rotation_euler', 2).driver
        if self.bounce:
            driver.expression = f'cos((frame - frame_start) * (2 * pi) / (1 + frame_end - frame_start)) * {self.rotations}'
        else:
            driver.expression = f'(frame - frame_start) * (2 * pi) / (1 + frame_end - frame_start) * {self.rotations}'

        # create frame start variable
        frame_start = driver.variables.new()
        frame_start.name = 'frame_start'
        frame_start.targets[0].id_type = 'SCENE'
        frame_start.targets[0].id = context.scene
        frame_start.targets[0].data_path = 'frame_start'

        # create frame end variable
        frame_end = driver.variables.new()
        frame_end.name = 'frame_end'
        frame_end.targets[0].id_type = 'SCENE'
        frame_end.targets[0].id = context.scene
        frame_end.targets[0].data_path = 'frame_end'

        # parent camera to empty
        cam.parent = empty

        # move camera into place
        cam.location.z = 6
        cam.location.y = -12

        # add constraint
        con = cam.constraints.new(type='DAMPED_TRACK')
        con.target = empty
        con.track_axis = 'TRACK_NEGATIVE_Z'

        if get_preferences().property.to_cam_jump:
            bpy.ops.view3d.view_camera()
            cam.select_set(True)
        
        # Operator UI
        if not HOPS_OT_camera_rig.called_ui:
            HOPS_OT_camera_rig.called_ui = True

            ui = Master()

            if self.bounce:
                word = "Bounce"
            else:
                word = "Camera"

            draw_data = [
                [f"{word} Turntable"],
                [" "],
                ["Numpad 0 to jump to Camera "],
                ["F9 to adjust settings "],
                ["Revolutions :" , self.rotations]
            ]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}


def register():
    register_class(HOPS_OT_camera_rig)


def unregister():
    unregister_class(HOPS_OT_camera_rig)
