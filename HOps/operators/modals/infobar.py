from bl_ui.space_statusbar import STATUSBAR_HT_header


def initiate(ot):
    STATUSBAR_HT_header.draw = infobar_main


def remove(ot):
    STATUSBAR_HT_header.draw = STATUSBAR_HT_header._draw_orig


def update(ot):
    STATUSBAR_HT_header.draw = infobar_main


def infobar_main(self, context):
    layout = self.layout
    row = self.layout.row(align=True)
    row.label(text="", icon='MOUSE_MOVE')
    row.separator()
    row.label(text="Adjust")

    row.separator(factor=20.0)

    row.label(text="", icon='MOUSE_LMB')
    row.separator()
    row.label(text="Confirm")

    row.separator(factor=20.0)

    row.label(text="", icon='MOUSE_RMB')
    row.separator()
    row.label(text="Cancel")

    row.separator(factor=20.0)

    row.label(text="", icon='EVENT_H')
    row.separator()
    row.label(text="Help")

    row.label(text="", icon='EVENT_M')
    row.separator()
    row.label(text="Modifiers")

    infobar_copiedlines(layout, context)


def infobar_copiedlines(layout, context):
    # print(layout.template_input_status())

    layout.separator_spacer()

    # messages
    layout.template_reports_banner()
    layout.template_running_jobs()

    layout.separator_spacer()

    # stats
    scene = context.scene
    view_layer = context.view_layer

    layout.label(text=scene.statistics(view_layer), translate=False)