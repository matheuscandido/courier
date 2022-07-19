import logging

from gi.repository import Gtk

from . import request_panel


class TabHandle(Gtk.HBox):
    def __init__(self, method: str, name: str, parent: Gtk.Widget, **properties):
        super().__init__(**properties)

        self.parent = parent

        self.method = method
        self.name = name

        self.title = Gtk.Label.new(self.build_tite(method, name))
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)

        close_button = Gtk.Button()
        close_button.set_image(icon)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect("clicked", self.on_tab_close)

        self.pack_start(self.title, expand=True, fill=True, padding=0)
        self.pack_end(close_button, expand=False, fill=False, padding=0)
        self.show_all()

    def on_tab_close(self, button: Gtk.Button):
        self.parent.remove_page(self.parent.get_current_page())

    def set_method(self, method: str):
        self.title.set_label(self.build_tite(method, self.name))

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.title.set_label(self.build_tite(self.method, name))

    def build_tite(self, method: str, name: str):
        self.method = method
        self.name = name
        return f"{method} - {name}"



class TabPanel(Gtk.Notebook):

    def __int__(self, **properties):
        super().__int__(**properties)
        self.set_scrollable(True)

    def new_tab(self, method: str, name: str, content: request_panel.RequestPanel):
        tab_handle = TabHandle(method=method, name=name, parent=self)

        content.set_tab_handle_ref(tab_handle)
        content.set_notebook_ref(self)

        page = Gtk.ScrolledWindow()
        page.add(content)
        self.append_page(page, tab_handle)
        self.set_tab_reorderable(page, True)
        self.show_all()


