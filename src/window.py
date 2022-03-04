# window.py
#
# Copyright 2021 Matheus Candido
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from .collection_manager import CollectionManager

from .tab_panel import TabPanel
from .request_panel import RequestPanel
from .sidebar import Sidebar

DEFAULT_SPACING = 5

METHOD = 0
NAME = 1

JSON_REQUESTS = (
    ("GET", "Get Item"),
    ("POST", "Create Item"),
    ("PUT", "Change Item"),
    ("PATCH", "Amend Item"),
    ("DELETE", "Delete Item")
)

# @Gtk.Template(resource_path='/com/mcandido/Courier/window.ui')
class CourierWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CourierWindow'

    #label = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_border_width(0)
        self.set_default_size(1200, 900)

        self.header_bar = Gtk.HeaderBar.new()
        self.setup_header_bar()
        self.set_titlebar(self.header_bar)

        hpaned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        hpaned.set_position(250)

        self.tab_panel = TabPanel()
        self.tab_panel.set_scrollable(True)
        self.tab_panel.new_tab("GET", "New Request", RequestPanel())

        self.collection_manager = CollectionManager()
        self.sidebar = Sidebar(self.collection_manager, self)

        hpaned.pack1(self.sidebar, False, False)
        hpaned.pack2(self.tab_panel, True, False)

        self.add(hpaned)
        self.set_size_request(225, 150)
        self.show_all()


    def setup_header_bar(self):
        self.header_bar.set_show_close_button(True)
        self.header_bar.set_custom_title(self.create_title_label())
        self.header_bar.pack_start(self.create_start_header_buttons())
        self.header_bar.pack_end(self.create_end_header_buttons())

    def create_title_label(self):
        return Gtk.Label("Courier")

    # def create_environment_list_component(self) -> Gtk.Widget:
    #     env_combo_box = Gtk.ComboBoxText.new()
    #     env_combo_box.append_text("Environment 1")
    #     env_combo_box.set_active(0)
    #     return env_combo_box

    def create_start_header_buttons(self) -> Gtk.Widget:
        start_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=DEFAULT_SPACING)
        new_tab_button = Gtk.Button.new_from_icon_name("tab-new-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        new_tab_button.connect("clicked", self.on_new_tab_button_clicked)
        import_button = Gtk.Button.new_with_label("Import")
        start_box.pack_start(new_tab_button, True, False, 0)
        start_box.pack_start(import_button, True, False, 0)
        return start_box

    def create_end_header_buttons(self) -> Gtk.Widget:
        new_menu_button = Gtk.Button.new_from_icon_name("open-menu", Gtk.IconSize.SMALL_TOOLBAR)
        return new_menu_button

    def on_new_tab_button_clicked(self, button: Gtk.Button):
        self.tab_panel.new_tab("GET", "New Request " + str(self.tab_panel.get_n_pages() + 1), RequestPanel())

