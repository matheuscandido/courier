from gi.repository import Gtk, GObject
from .collection_manager import CollectionManager
from . import constants
from .request_panel import RequestPanel

from json import dumps, loads

import logging

TYPE = 0
METHOD = 1
NAME = 2
REQUEST_JSON_STRING = 3

TREE_COLLECTION = 0
TREE_REQUEST = 1

METHOD_COLORS = {
    "GET": "#22FF00",
    "POST": "#FFEE00",
    "PUT": "#0055FF",
    "PATCH": "#000000",
    "DELETE": "#FF0000"
}

class Sidebar(Gtk.ScrolledWindow):

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
        self.model_store = Gtk.TreeStore.new((
            GObject.TYPE_BOOLEAN, # type
            GObject.TYPE_STRING,  # method
            GObject.TYPE_STRING,  # name
            GObject.TYPE_STRING,  # request json string
        ))

        for collection in self.collection_manager.colletions:
            root_iter: Gtk.TreeIter = self.model_store.append(None)
            self.model_store.set(root_iter, TYPE, TREE_COLLECTION, METHOD, "", NAME, collection["info"]["name"])

            for item in collection["item"]:
                self.iterative_collection_parser(self.model_store, root_iter, item)

        self.tree_view.set_model(self.model_store)

        self.add(self.tree_view)



    def iterative_collection_parser(self, model_store: Gtk.TreeStore, parent_iter: Gtk.TreeIter, item: dict):
        if "request" in item:
            # item is a request
            item_iter = model_store.append(parent_iter)
            model_store.set(item_iter,
                TYPE, TREE_REQUEST,
                METHOD, item["request"]["method"],
                NAME, item["name"],
                REQUEST_JSON_STRING, dumps(item))
            return
        else:
            # item is a folder
            item_iter = model_store.append(parent_iter)
            model_store.set(item_iter,
                TYPE, TREE_COLLECTION,
                METHOD, "",
                NAME, item["name"],
                REQUEST_JSON_STRING, "")
            for child in item["item"]:
                self.iterative_collection_parser(
                    model_store=model_store,
                    parent_iter=item_iter,
                    item=child
                )
    
    def setup_tree_view(self):
        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Method", renderer, text=METHOD)
        column.set_cell_data_func(renderer, self.cell_data_method_column)
        self.tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Name", renderer, text=NAME)
        self.tree_view.append_column(column)

    def cell_data_method_column(self, column, renderer, model, iter, data):
        (method,) = model.get(iter, METHOD)
        renderer.props.foreground = self.get_method_color(method)

    def on_row_activated_signal(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        model: Gtk.TreeModel = treeview.get_model()
        iter = model.get_iter(path)
        if iter:
            (row_type, method, name, request_json_string) = model.get(iter, TYPE, METHOD, NAME,  REQUEST_JSON_STRING)
            if row_type == TREE_COLLECTION:
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
        if method in METHOD_COLORS:
            return METHOD_COLORS[method]
        else:
            return "#FFFFFF"

