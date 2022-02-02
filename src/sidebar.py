from gi.repository import Gtk, GObject
from .collection_manager import CollectionManager
from . import constants

TYPE = 0
METHOD = 1
NAME = 2

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
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING
        ))

        for collection in self.collection_manager.colletions:
            self.recursive_collection_parser(self.model_store, None, collection)

        # for collection in self.collection_manager.colletions:
        #     root_iter = self.model_store.append(None)
        #     self.model_store.set(root_iter, TYPE, TREE_COLLECTION, METHOD, "", NAME, collection["info"]["name"])

        #     parent_iter = root_iter

        #     for item in collection["item"]:
        #         item_iter = self.model_store.append(parent_iter)
        #         self.model_store.set(item_iter, TYPE, TREE_REQUEST, METHOD, item["request"]["method"], NAME, item["name"])

        self.tree_view.set_model(self.model_store)

        self.add(self.tree_view)

    def recursive_collection_parser(self, model_store, parent_iter, item: dict):
        if "item" in item:
            item_iter = model_store.append(parent_iter)
            if parent_iter is None:
                model_store.set(item_iter, TYPE, TREE_COLLECTION, METHOD, "", NAME, item["info"]["name"])
            else:
                model_store.set(item_iter, TYPE, TREE_COLLECTION, METHOD, "", NAME, item["name"])

            for i in item["item"]:
                self.recursive_collection_parser(model_store, item_iter, i)
        else:
            item_iter = model_store.append(parent_iter)
            model_store.set(parent_iter, TYPE, TREE_REQUEST, METHOD, item["request"]["method"], NAME, item["name"])
            print(f"adicionou {item['name']} filho de {parent_iter}")
    
    def setup_tree_view(self):
        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Name", renderer, text=NAME)
        self.tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Method", renderer, text=METHOD)
        column.set_cell_data_func(renderer, self.cell_data_method_column)
        self.tree_view.append_column(column)

    def cell_data_method_column(self, column, renderer, model, iter, data):
        (method,) = model.get(iter, METHOD)
        renderer.props.foreground = self.get_method_color(method)

    def on_row_activated_signal(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        model: Gtk.TreeModel = treeview.get_model()
        iter = model.get_iter(path)
        if iter:
            (row_type, method, name) = model.get(iter, TYPE, METHOD, NAME)
            if row_type == TREE_COLLECTION:
                return

            if len(name) > 15:
                name = name[:15] + "..."
            self.window.tab_panel.new_tab(f"{method} {name}", RequestPanel(method=method))

    def get_method_color(self, method: str) -> str:
        if method in METHOD_COLORS:
            return METHOD_COLORS[method]
        else:
            return "#FFFFFF"

