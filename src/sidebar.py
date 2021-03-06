from gi.repository import Gtk, GObject
from .collection_manager import CollectionManager
from . import constants as consts
from .request_panel import RequestPanel
from typing import List

import json
import logging

@Gtk.Template(resource_path='/com/mcandido/Courier/ui/sidebar.ui')
class Sidebar(Gtk.ScrolledWindow):
    __gtype_name__ = 'Sidebar'

    def __init__(self, window: Gtk.ApplicationWindow):
        from .window import CourierWindow
        super().__init__()
        self.window: CourierWindow = window
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.tree_view = Gtk.TreeView.new()
        self.setup_tree_view()
        self.tree_view.connect("row-activated", self.on_row_activated_signal)

        self.model_store = Gtk.TreeStore.new((
            GObject.TYPE_BOOLEAN, # type
            GObject.TYPE_STRING,  # info
            GObject.TYPE_STRING,  # method
            GObject.TYPE_STRING,  # name
            GObject.TYPE_STRING,  # request json string
        ))

        self.tree_view.set_model(self.model_store)

        self.add(self.tree_view)
        self.show_all()

    # def reload_collections(self):
    #     self.model_store = self.collection_manager.get_collections_tree_store()
    #     self.tree_view.set_model(self.model_store)

    def setup_tree_view(self):
        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Method", renderer, text=consts.METHOD)
        column.set_cell_data_func(renderer, self.cell_data_method_column)
        self.tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Name", renderer, text=consts.NAME)
        self.tree_view.append_column(column)

    def store_data_to_disk(self):
        self.window.save_model_store(self.model_store)

    def cell_data_method_column(self, column, renderer, model, iter, data):
        (method,) = model.get(iter, consts.METHOD)
        renderer.props.foreground = self.get_method_color(method)

    def on_row_activated_signal(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        model: Gtk.TreeModel = treeview.get_model()
        iter = model.get_iter(path)
        if iter:
            (row_type, method, name, request_json_string) = model.get(iter, consts.TYPE, consts.METHOD, consts.NAME, consts.REQUEST_JSON_STRING)
            if row_type == consts.TREE_COLLECTION:
                return

            if len(name) > 15:
                name = name[:15] + "..."
            request_json_dict = json.loads(request_json_string)

            if "body" in request_json_dict["request"]:
                body = request_json_dict["request"]["body"]["raw"]
            else:
                body = ""

            headers = [(obj["key"], obj["value"]) for obj in request_json_dict["request"]["header"]] if "header" in request_json_dict["request"] else []

            req_panel = RequestPanel(
                method=method,
                url=request_json_dict["request"]["url"]["raw"],
                body=body,
                headers=headers,
                sidebar=self,
                tree_store=model,
                tree_iter=iter)
            self.window.tab_panel.new_tab(method, name, req_panel)

    def get_method_color(self, method: str) -> str:
        if method in consts.METHOD_COLORS:
            return consts.METHOD_COLORS[method]
        else:
            return "#FFFFFF"

    def add_collections_to_model(self, collections: List[dict]):
        for collection in collections:
            root_iter: Gtk.TreeIter = self.model_store.append(None)
            self.model_store.set(root_iter, 
                consts.TYPE, consts.TREE_COLLECTION, 
                consts.INFO, json.dumps(collection["info"]), 
                consts.METHOD, "", 
                consts.NAME, collection["info"]["name"]
            )

            for item in collection["item"]:
                self._recursive_collection_parser(self.model_store, root_iter, item)
    
    def _recursive_collection_parser(self, model_store: Gtk.TreeStore, parent_iter: Gtk.TreeIter, item: dict):
            if "request" in item:
                # item is a request
                item_iter = model_store.append(parent_iter)
                model_store.set(item_iter,
                    consts.TYPE, consts.TREE_REQUEST,
                    consts.METHOD, item["request"]["method"],
                    consts.NAME, item["name"],
                    consts.REQUEST_JSON_STRING, json.dumps(item))
                return
            else:
                # item is a folder
                item_iter = model_store.append(parent_iter)
                model_store.set(item_iter,
                    consts.TYPE, consts.TREE_COLLECTION,
                    consts.METHOD, "",
                    consts.NAME, item["name"],
                    consts.REQUEST_JSON_STRING, "")
                for child in item["item"]:
                    self._recursive_collection_parser(
                        model_store=model_store,
                        parent_iter=item_iter,
                        item=child
                    )

