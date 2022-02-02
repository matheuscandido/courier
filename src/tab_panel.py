import logging

from gi.repository import Gtk


class TabHandle(Gtk.HBox):
    def __init__(self, title: str, parent: Gtk.Widget, **properties):
        super().__init__(**properties)

        self.parent = parent
        title = Gtk.Label.new(title)
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)

        close_button = Gtk.Button()
        close_button.set_image(icon)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect("clicked", self.on_tab_close)

        self.pack_start(title, expand=True, fill=True, padding=0)
        self.pack_end(close_button, expand=False, fill=False, padding=0)
        self.show_all()

    def on_tab_close(self, button: Gtk.Button):
        self.parent.remove_page(self.parent.get_current_page())


class TabPanel(Gtk.Notebook):

    def __int__(self, **properties):
        super().__int__(**properties)
        self.set_scrollable(True)

    def new_tab(self, title: str, content: Gtk.Widget):
        tab_handle = TabHandle(title=title, parent=self)
        page = Gtk.ScrolledWindow()
        page.add(content)
        self.append_page(page, tab_handle)
        self.set_tab_reorderable(page, True)
        self.show_all()


