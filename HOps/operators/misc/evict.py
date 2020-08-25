import bpy
from ...utility.collections import link_obj, unlink_obj
from ... preferences import get_preferences
from ...ui_framework.operator_ui import Master


class HOPS_OT_EVICT(bpy.types.Operator):
    bl_idname = "hops.evict"
    bl_label = "Evict / Unify Cutters"
    bl_options = {"REGISTER", 'UNDO'}
    bl_description = """Unify. Pull all solid/textured shapes into collection of active object
CTRL - Evict cutters from selection into Cutters collection
"""

    called_ui = False
    text = 'none'

    def __init__(self):

        HOPS_OT_EVICT.called_ui = False

    @classmethod
    def poll(cls, context):
        return True

    def invoke (self, context, event):
        self.unify = False if event.ctrl else True
        return self.execute(context)

    def execute(self, context):
        hops_coll = "Cutters"
        collections = context.scene.collection.children
        view_collections = context.view_layer.layer_collection.children

        if self.unify and context.active_object:
            shapes = [obj for obj in context.scene.objects if obj.type == 'MESH' and  obj.display_type not in {'WIRE', 'BOUNDS'} and not obj.hide_get() and obj != context.active_object]
            shape_count = 0
            for shape in shapes:
                shape_count += 1
                full_unlink(shape)
                link_to_active(shape, context.active_object)
        else:
            evicted_cutters = 0
            cutters = [obj for obj in context.selected_objects if (obj.type == 'MESH' and obj.display_type in {'WIRE', 'BOUNDS'}) or (obj.type == 'EMPTY' and not obj.is_instancer)]
            evicted_cutters += len(cutters)
            for cutter in cutters:
                full_unlink( cutter)
                link_obj(context, cutter)
            if hops_coll in view_collections:
                view_collections[hops_coll].hide_viewport = True
            print(F"Cutters evicted:{evicted_cutters}")

        if self.unify:
            text = 'Unify'
            substat = shape_count
            info = 'Amount Unified'
        else:
            text = 'Evict'
            substat = evicted_cutters
            info = 'Amount Evicted'

        # Operator UI
        if not HOPS_OT_EVICT.called_ui:
            HOPS_OT_EVICT.called_ui = True

            ui = Master()
            draw_data = [
                [text],
                [info, substat]]
            ui.receive_draw_data(draw_data=draw_data)
            ui.draw(draw_bg=get_preferences().ui.Hops_operator_draw_bg, draw_border=get_preferences().ui.Hops_operator_draw_border)

        return {"FINISHED"}

def full_unlink (obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)

def link_to_active(obj, active ):
    for col in active.users_collection:
        col.objects.link(obj)
