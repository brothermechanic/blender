import bpy
import bmesh
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from bpy.props import StringProperty, EnumProperty, PointerProperty, IntProperty, BoolProperty, FloatProperty

class HOPS_OT_DisplayNotification(bpy.types.Operator):
    bl_idname = "hops.display_notification"
    bl_label = "Displays a notification for an action"
    bl_options = {'REGISTER'}
    bl_description = """Displays a notification

"""

    info: StringProperty(name="Notification Header", default='Insert Notification Here')
    name: StringProperty(name="Header Name", default='hardOps')

    called_ui = False

    def __init__(self):

        HOPS_OT_DisplayNotification.called_ui = False

    def execute(self, context):

        
        # Operator UI
        if not HOPS_OT_DisplayNotification.called_ui:
            HOPS_OT_DisplayNotification.called_ui = True

            ui = Master()

            draw_data = [
                [self.info]
                ]

            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        if self.info != 'Insert Notification Here':
            return {"RUNNING_MODAL"}
        else:
            return {'FINISHED'}