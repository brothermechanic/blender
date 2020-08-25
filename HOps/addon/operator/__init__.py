import bpy


from . import modifier, add, select, tool, topbar, shape, camera


def register():
    shape.register()
    modifier.register()
    add.register()
    select.register()
    tool.register()
    topbar.register()
    camera.register()


def unregister():
    modifier.unregister()
    add.unregister()
    select.unregister()
    tool.unregister()
    topbar.unregister()
    shape.unregister()
    camera.unregister()
