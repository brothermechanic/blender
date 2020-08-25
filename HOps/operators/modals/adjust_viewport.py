import bpy
from math import radians
import math
from ... utils.blender_ui import get_dpi_factor
from ... preferences import get_preferences
from ... ui_framework.master import Master
from . import infobar
from ... utility.base_modal_controls import Base_Modal_Controls

class HOPS_OT_AdjustViewport(bpy.types.Operator):
    bl_idname = 'hops.adjust_viewport'
    bl_label = 'Adjust Viewport'
    bl_description = 'Adjust the viewport settings'
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    eeveeHQ = 'None'

    to_render = 'None'

    def __init__(self):
        self.master = None


    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

#alright this thing is pretty close to being done. I don't need corrections. Just completions
#improve it if you want but the goals are the same with this modal.

    def invoke(self, context, event):
        self.shading = context.space_data.shading
        wm = bpy.context.window_manager
        # if hasattr(wm, 'cycles'):
        #     bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        if (2, 83, 0) < bpy.app.version:
            self.shading_args = {'type', 'studio_light', 'studiolight_rotate_z', 'studiolight_intensity', 'studiolight_background_alpha', 'studiolight_background_blur'}
        else:
            self.shading_args = {'type', 'studio_light', 'studiolight_rotate_z', 'studiolight_intensity', 'studiolight_background_alpha'}
        self.shading_dict = self.save(self.shading, self.shading_args)
        self.envs = [img.name for img in context.preferences.studio_lights if img.type == 'WORLD']
        self.original_opacity = self.shading.studiolight_background_alpha
        self.original_viewport = bpy.context.space_data.overlay.show_overlays
        self.original_mode = self.shading.type
        self.original_exr = self.shading.studio_light

        #type has to change before indexing or it bricks
        self.shading.type = 'MATERIAL'
        self.shading.studiolight_background_alpha = 1
        self.hdri_index = self.envs.index(self.shading.studio_light)
        self.hdri_index_max = len(self.envs) -1
        if bpy.context.region_data.is_perspective:
            self.viewmode = False
        else:
            self.viewmode = True
            bpy.ops.view3d.view_persportho()
            #print("Ortho")

        if get_preferences().property.to_render_jump:
            self.to_render = True
        else:
            self.to_render = 'None'
        self.base_controls = Base_Modal_Controls(context, event)


        if (2, 83, 0) < bpy.app.version:
            self.modes = ('Background Rotate', 'Background Blur', 'Background Strength', 'Background Opacity')
        else:
            self.modes = ('Background Rotate', 'Background Strength', 'Background Opacity')


        self.mode = self.modes[0]

        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        context.area.header_text_set(text='Adjust Viewport')
        context.window_manager.modal_handler_add(self)
        infobar.initiate(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        if self.base_controls.mouse:


            offset = self.base_controls.mouse * 10

            # TODO: Use buffer variables and rounding

            if self.mode == 'Background Rotate':
                if self.shading.studiolight_rotate_z + offset > radians(180):
                    self.shading.studiolight_rotate_z = radians(-180)
                elif self.shading.studiolight_rotate_z + offset < radians(-180):
                    self.shading.studiolight_rotate_z = radians(180)
                self.shading.studiolight_rotate_z += offset
            elif self.mode == 'Background Strength':
                self.shading.studiolight_intensity += offset# / 2
            elif self.mode == 'Background Opacity':
                self.shading.studiolight_background_alpha += offset# / 5
            elif self.mode == 'Background Blur' and (2, 83, 0) < bpy.app.version:
                self.shading.studiolight_background_blur += offset# / 5

        elif self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        elif event.type == 'TAB' and event.value == 'PRESS':
            context.space_data.overlay.show_overlays = not context.space_data.overlay.show_overlays

        elif event.type == 'X' and event.value == 'PRESS':
            index = self.modes.index(self.mode)
            index = (index + 1) % len(self.modes)
            self.mode = self.modes[index]

        elif event.type == 'W' and event.value == 'PRESS' and (event.shift or event.alt):
            context.space_data.overlay.show_overlays = False
            self.shading.studiolight_intensity = 1
            self.shading.studiolight_background_alpha = 1

            if (2, 83, 0) < bpy.app.version:
                self.shading.studiolight_background_blur = 0
            self.mode = self.modes[0]
            pass

        elif event.type == 'W' and event.value == 'PRESS':
            context.space_data.overlay.show_overlays = False
            self.shading.studiolight_intensity = 1
            self.shading.studiolight_background_alpha = 1
            #if (2, 83, 0) < bpy.app.version:
            #    self.shading.studiolight_background_blur = 0
            self.mode = self.modes[0]
            if self.eeveeHQ:
                bpy.ops.render.setup()
                self.eeveeHQ = True
            else:
                bpy.ops.renderb.setup()
                self.eeveeHQ = False
            self.eeveeHQ = not self.eeveeHQ
            pass

        elif (event.type == 'WHEELUPMOUSE' and event.shift) or (event.type in {'NUMPAD_PLUS', 'EQUAL', 'S' , 'UP_ARROW'} and event.value == 'PRESS'):
            if event.ctrl:
                index = self.modes.index(self.mode)
                index = (index - 1) % len(self.modes)
                self.mode = self.modes[index]

            else:
                self.hdri_index = self.hdri_index +1 if self.hdri_index != self.hdri_index_max else 0
                #self.shading.studio_light = next_list_item(self.envs, self.shading.studio_light)
                self.shading.studio_light = self.envs[self.hdri_index]
            pass # TODO: change environment

        elif (event.type == 'WHEELDOWNMOUSE' and event.shift) or (event.type in {'NUMPAD_MINUS', 'MINUS', 'A', 'DOWN_ARROW'} and event.value == 'PRESS'):
            if event.ctrl:
                index = self.modes.index(self.mode)
                index = (index + 1) % len(self.modes)
                self.mode = self.modes[index]

            else:
                self.hdri_index = self.hdri_index -1 if self.hdri_index !=0 else self.hdri_index_max
               # self.shading.studio_light = previous_list_item(self.envs, self.shading.studio_light)
                self.shading.studio_light = self.envs[self.hdri_index]
            pass # TODO: change environment

        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}



        #there could probably be more states saved for restoring on start and cancel.
        #dont integrate random ideas at this time. Lets get it ready and plan for the future.
        elif self.base_controls.cancel:
            #mode has to be restored before hdri it it breaks
            bpy.context.space_data.shading.type = self.original_mode
            self.load(self.shading, self.shading_dict)
            bpy.context.space_data.overlay.show_overlays = self.original_viewport
            # bpy.context.space_data.shading.studio_light = self.original_exr
            # self.shading.studiolight_background_alpha = self.original_opacity



            #bpy.context.space_data.shading.type = 'SOLID'
            if self.viewmode:
                bpy.ops.view3d.view_persportho()
            context.area.header_text_set(text=None)
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'CANCELLED'}

        elif self.base_controls.confirm:
            context.area.header_text_set(text=None)
            #self.shading.studiolight_background_alpha = self.original_opacity
            #bpy.context.space_data.overlay.show_overlays = self.original_viewport
            #if self.viewmode:
            #    bpy.ops.view3d.view_persportho()
            if self.to_render == True:
                set_render(self,context)
                self.report({'INFO'}, F'Render Set To Lookdev')
            context.window_manager.event_timer_remove(self.timer)
            self.master.run_fade()
            infobar.remove(self)
            return {'FINISHED'}

        elif (event.type == 'P' or event.type == 'NUMPAD_5') and event.value == 'PRESS':
            bpy.ops.view3d.view_persportho()

        elif event.type == 'Z' and event.value == 'PRESS':
            bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes
            bpy.context.space_data.overlay.wireframe_threshold = 1

        elif event.type == 'B' and event.value == 'PRESS':
            if (2, 83, 0) < bpy.app.version:
                self.shading.studiolight_background_blur = 0 if self.shading.studiolight_background_blur > 0 else 1
            else:
                self.report({'INFO'}, F'Requires 2.83')
                pass

        elif event.type == 'V' and event.value == 'PRESS':
            self.shading.studiolight_background_alpha = 0 if self.shading.studiolight_background_alpha > 0 else 1

        elif event.type == 'C' and event.value == 'PRESS':
            self.shading.studiolight_intensity = 0 if self.shading.studiolight_intensity > 0 else 1

        elif event.type == 'R' and event.value == 'PRESS':
            if self.to_render == 'None':
                self.to_render = True
                self.report({'INFO'}, F'Render Set To {self.to_render}')
            else:
                self.to_render = not self.to_render
                self.report({'INFO'}, F'Render Set To {self.to_render}')

        elif event.type == 'M' and event.value == 'PRESS' and event.ctrl:
            if bpy.context.selected_objects:
                context.area.header_text_set(text=None)
                self.shading.studiolight_background_alpha = self.original_opacity
                bpy.context.space_data.overlay.show_overlays = self.original_viewport
                if self.viewmode:
                    bpy.ops.view3d.view_persportho()
                bpy.ops.hops.material_scroll('INVOKE_DEFAULT')
                context.window_manager.event_timer_remove(self.timer)
                self.master.run_fade()
                infobar.remove(self)
                return {'FINISHED'}
            else:
                self.report({'INFO'}, F'No selection bud')
                pass

        elif event.type == 'Q' and event.value == 'PRESS':
            bpy.context.scene.eevee.use_bloom = not bpy.context.scene.eevee.use_bloom
            bpy.context.scene.eevee.bloom_intensity = 1.04762
            bpy.context.scene.eevee.bloom_threshold = 1.94286
            self.report({'INFO'}, F'Bloom: {bpy.context.scene.eevee.use_bloom}')


        self.draw_master(context=context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def save(self, data, args: set):
        return {arg: getattr(data, arg) for arg in args}

    def load(self, data, args: dict):
        for key, value in args.items():
            setattr(data, key, value)

    def finish(self, context):
        context.area.header_text_set(text=None)
        self.remove_ui()
        infobar.remove(self)
        return {"FINISHED"}


    def draw_master(self, context):
        self.master.setup()

        if self.master.should_build_fast_ui():
            win_list = []
            help_list = []
            mods_list = []
            active_mod = ''

            #Micro UI
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(f'{self.mode[11:]}')

                if self.mode == 'Background Rotate':
                    win_list.append(f'{math.degrees(self.shading.studiolight_rotate_z):.0f}°')
                elif self.mode == 'Background Strength':
                    win_list.append(f'{self.shading.studiolight_intensity:.3f}')
                elif self.mode == 'Background Opacity':
                    win_list.append(f'{self.shading.studiolight_background_alpha:.3f}')
                elif self.mode == 'Background Blur' and (2, 83, 0) < bpy.app.version:
                    win_list.append(f'{self.shading.studiolight_background_blur:.3f}')

                if self.eeveeHQ == 'None':
                    pass
                    #win_list.append(f'General')
                elif self.eeveeHQ != False:
                    win_list.append(f'LQ')
                elif self.eeveeHQ == False:
                    win_list.append(f'HQ')

                if self.to_render != 'None':
                    win_list.append(f'[R] To_Render {self.to_render}')

            #Full UI
            else:
                win_list.append('Viewport')

                win_list.append(f'Mode: {self.mode}')

                if self.mode == 'Background Rotate':
                    win_list.append(f'Angle: {math.degrees(self.shading.studiolight_rotate_z):.0f}')
                elif self.mode == 'Background Strength':
                    win_list.append(f'Strength: {self.shading.studiolight_intensity:.3f}')
                elif self.mode == 'Background Opacity':
                    win_list.append(f'Opacity: {self.shading.studiolight_background_alpha:.3f}')
                elif self.mode == 'Background Blur' and (2, 83, 0) < bpy.app.version:
                    win_list.append(f'Blur: {self.shading.studiolight_background_blur:.3f}')

                if self.eeveeHQ == 'None':
                    win_list.append(f'[W] General')
                elif self.eeveeHQ != False:
                    win_list.append(f'[W] Eevee LQ')
                elif self.eeveeHQ == False:
                    win_list.append(f'[W] Eevee HQ')

                if self.to_render != 'None':
                    win_list.append(f'[R] To_Render {self.to_render}')


            help_list.append(['NUM 5 / P',  'Toggle Persp/Ortho'])
            help_list.append(['Tab',        'Toggle overlays'])
            if bpy.context.selected_objects:
                help_list.append(['Ctrl + M',   'Blank Material - Exit'])
            else:
                help_list.append(['',       'No Selection Active'])
            help_list.append(['V',          'Background Alpha'])
            help_list.append(['C',          'Intensity'])
            if (2, 83, 0) < bpy.app.version:
                help_list.append(['B',          'Blur'])
            else:
                help_list.append(['B',          'Blur (UPDATE BLENDER)'])
            help_list.append(['Q',          'Bloom'])
            help_list.append(['X',          'Cycle adjust mode'])
            help_list.append(['W',          f'Eevee LQ / HQ '])
           # help_list.append(['RMB',        'SOLID view - exit'])
            help_list.append(['RMB/ESC',    'Cancel'])
            help_list.append(['Shift + W',  f'Reset View '])
            help_list.append(['-/+ / A/S',  'Scroll Environment'])
            help_list.append(['Shift + MMB','Scroll Environment'])
            help_list.append(['R',          'Set View To Render'])
            help_list.append(['H',          'Toggle help'])
            help_list.append(['~',          'Toggle viewport displays'])

            # # todo Instead of mods list the envinrments and go through them
            # if bpy.context.selected_objects:
            #     for mod in reversed(context.active_object.modifiers):
            #         mods_list.append([mod.name, str(mod.type)])
            mods_list=[ [e,""] for e in self.envs]


            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image='WireMode', mods_list=mods_list,  active_mod_name=self.shading.studio_light)

        self.master.finished()

def next_list_item(list, current):
    index = list.index(current)
    return list[0] if index + 1 > len(list) - 1 else list[index + 1]

def previous_list_item(list, current):
    index = list.index(current)
    return list[-1] if index - 1 < 0 else list[index - 1]

def set_render(self, context):

    self.shading = context.space_data.shading
    active_hdri_name =  self.shading.studio_light

    img_path = bpy.context.preferences.studio_lights[active_hdri_name].path

    img = bpy.data.images.load(img_path, check_existing =True )

    world = bpy.data.worlds.new(active_hdri_name)
    world.use_nodes = True
    bpy.context.scene.world = world

    world_node_tree = bpy.context.scene.world.node_tree
    world_nodes = world.node_tree.nodes

    background_shader = world_nodes['Background']
    background_shader.inputs['Strength'].default_value = self.shading.studiolight_intensity
    y_loc = background_shader.location[1]

    hdri_node = world_nodes.new('ShaderNodeTexEnvironment')
    hdri_node.image = img

    offset = hdri_node.width
    hdri_node.location = [-offset, y_loc]

    mapping_node = world_nodes.new("ShaderNodeMapping")
    mapping_node.inputs['Rotation'].default_value[2] = self.shading.studiolight_rotate_z
    mapping_node.location = [-offset*2, y_loc]

    text_coord_node = world_nodes.new("ShaderNodeTexCoord")
    text_coord_node.location= [-offset*3, y_loc]

    world_node_tree.links.new(background_shader.inputs[0], hdri_node.outputs[0])
    world_node_tree.links.new(hdri_node.inputs[0] ,mapping_node.outputs[0]  )
    world_node_tree.links.new(mapping_node.inputs['Vector'] , text_coord_node.outputs['Generated']  )
