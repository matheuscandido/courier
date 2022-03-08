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

@Gtk.Template(resource_path='/com/mcandido/Courier/ui/main_window.ui')
class CourierWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CourierWindow'

    header_bar = Gtk.Template.Child()
    hpaned = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.tab_panel = TabPanel()
        self.tab_panel.set_scrollable(True)
        self.tab_panel.new_tab("GET", "New Request", RequestPanel())

        self.collection_manager = CollectionManager()
        self.sidebar = Sidebar(self.collection_manager, self)
        self.sidebar.set_visible(True)
        
        self.hpaned.pack1(self.sidebar, False, False)
        self.hpaned.pack2(self.tab_panel, True, False)

    @Gtk.Template.Callback()
    def on_new_tab_button_clicked(self, button: Gtk.Button):
        self.tab_panel.new_tab("GET", "New Request " + str(self.tab_panel.get_n_pages() + 1), RequestPanel())

