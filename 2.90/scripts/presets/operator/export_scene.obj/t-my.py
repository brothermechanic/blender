import bpy
op = bpy.context.active_operator

op.filepath = '/media/disk/mult/town/cars/export/c-hp.obj'
op.use_selection = True
op.use_animation = False
op.use_mesh_modifiers = True
op.use_edges = True
op.use_smooth_groups = False
op.use_smooth_groups_bitflags = False
op.use_normals = True
op.use_uvs = True
op.use_materials = True
op.use_triangles = False
op.use_nurbs = False
op.use_vertex_groups = False
op.use_blen_objects = True
op.group_by_object = False
op.group_by_material = False
op.keep_vertex_order = False
op.global_scale = 1000.0
op.path_mode = 'AUTO'
op.axis_forward = 'Y'
op.axis_up = 'Z'
