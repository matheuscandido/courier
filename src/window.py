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

from logging import log
from gi.repository import Gtk, Gio
from .collection_manager import CollectionManager

from .tab_panel import TabPanel
from .request_panel import RequestPanel
from .sidebar import Sidebar

import threading
import json

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
    import_button = Gtk.Template.Child()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.tab_panel = TabPanel()
        self.tab_panel.set_scrollable(True)
        self.tab_panel.new_tab("GET", "New Request", RequestPanel())

        self.collection_manager = CollectionManager()
        self.sidebar = Sidebar(self.collection_manager, self)
        self.sidebar.set_visible(True)

        collections = self.collection_manager.load_collections_from_disk()
        self.sidebar.add_collections_to_model(collections)
        
        self.hpaned.pack1(self.sidebar, False, False)
        self.hpaned.pack2(self.tab_panel, True, False)

    @Gtk.Template.Callback()
    def on_new_tab_button_clicked(self, button: Gtk.Button):
        self.tab_panel.new_tab("GET", "New Request " + str(self.tab_panel.get_n_pages() + 1), RequestPanel())

    @Gtk.Template.Callback()
    def on_import_button_clicked(self, button: Gtk.Button):
        dialog = Gtk.FileChooserDialog(title="Import Collection", parent=self, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        self._add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file: Gio.File = dialog.get_file()
            success , contents, etag_out = file.load_contents()

            if success:
                thread = threading.Thread(
                    target=self._import_new_collection, 
                    kwargs={"file": contents.decode('utf-8')}
                    )
                thread.daemon = True
                thread.start()

        elif response == Gtk.ResponseType.CANCEL:
            print("Import canceled")
        dialog.destroy()

    def _add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("JSON files")
        filter_py.add_mime_type("text/x-json")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def _import_new_collection(self, file: str):
        self.sidebar.add_collections_to_model(
            [self.collection_manager.load_collection(file)]
            )
