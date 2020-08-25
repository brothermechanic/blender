import bpy
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master
from ... utility import addon

class HOPS_OT_TP_PowerSaveInt(bpy.types.Operator):
    bl_idname = "hops.powersave"
    bl_label = "PowerSave"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Save this blend file with the name in the text field below.
If no name is provided, generate one based on the date and time.
If this blend has never been saved, put it in the PowerSave folder"""

    called_ui = False

    def __init__(self):
        HOPS_OT_TP_PowerSaveInt.called_ui = False

    def invoke(self, context, event):
        #self.keep_sharp = False if event.shift else True
        return self.execute(context)

    def execute(self, context):
        try:
            bpy.ops.powersave.powersave()
        except:
            pass

        # Operator UI
        if not HOPS_OT_TP_PowerSaveInt.called_ui:
            HOPS_OT_TP_PowerSaveInt.called_ui = True

            ui = Master()
            draw_data = [
                ["PowerSave"],
                [addon.powersave().base_folder, " "],
                [addon.powersave().powersave_name, " "],
                ["Now saving ... ", " "]
            ]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}
