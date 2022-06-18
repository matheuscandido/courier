from gi.repository import Gtk, GObject
from .collection_manager import CollectionManager
from . import constants
from .request_panel import RequestPanel

from json import dumps, loads

import logging

@Gtk.Template(resource_path='/com/mcandido/Courier/ui/sidebar.ui')
class Sidebar(Gtk.ScrolledWindow):
    __gtype_name__ = 'Sidebar'

    def __init__(self, collection_manager: CollectionManager, window: Gtk.ApplicationWindow):
        super().__init__()
        self.window = window
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.collection_manager = collection_manager
        self.collection_manager.load_all_collections()

        self.tree_view = Gtk.TreeView.new()
        self.setup_tree_view()
        self.tree_view.connect("row-activated", self.on_row_activated_signal)

        # Type, Method, Method
        self.model_store = self.collection_manager.get_collections_tree_store()
        self.tree_view.set_model(self.model_store)

        self.add(self.tree_view)
        self.show_all()

    def reload_collections(self):
        self.model_store = self.collection_manager.get_collections_tree_store()
        self.tree_view.set_model(self.model_store)

    def setup_tree_view(self):
        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Method", renderer, text=constants.METHOD)
        column.set_cell_data_func(renderer, self.cell_data_method_column)
        self.tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Name", renderer, text=constants.NAME)
        self.tree_view.append_column(column)

    def cell_data_method_column(self, column, renderer, model, iter, data):
        (method,) = model.get(iter, constants.METHOD)
        renderer.props.foreground = self.get_method_color(method)

    def on_row_activated_signal(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        model: Gtk.TreeModel = treeview.get_model()
        iter = model.get_iter(path)
        if iter:
            (row_type, method, name, request_json_string) = model.get(iter, constants.TYPE, constants.METHOD, constants.NAME,  constants.REQUEST_JSON_STRING)
            if row_type == constants.TREE_COLLECTION:
                return

            if len(name) > 15:
                name = name[:15] + "..."
            request_json_dict = loads(request_json_string)

            if "body" in request_json_dict["request"]:
                body = request_json_dict["request"]["body"]["raw"]
            else:
                body = ""

            headers = [(obj["key"], obj["value"]) for obj in request_json_dict["request"]["header"]] if "header" in request_json_dict["request"] else []

            req_panel = RequestPanel(
                method=method,
                url=request_json_dict["request"]["url"]["raw"],
                body=body,
                headers=headers)
            self.window.tab_panel.new_tab(method, name, req_panel)

    def get_method_color(self, method: str) -> str:
        if method in constants.METHOD_COLORS:
            return constants.METHOD_COLORS[method]
        else:
            return "#FFFFFF"

