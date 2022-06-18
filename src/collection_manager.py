from pathlib import Path
import json
import os
from typing import List

from gi.repository import Gtk, GObject
from . import constants as consts

class CollectionManager:

    def __init__(self) -> None:
        self.collections: List[dict] = []
        
        # Check if coutier dir exists, creates if not
        if not os.path.exists(consts.CONFIG_PATH):
            os.mkdir(consts.CONFIG_PATH)

    def load_all_collections(self) -> List[dict]:
        json_files = [f for f in os.listdir(consts.CONFIG_PATH) if f.endswith(".json")]
        for fl in json_files:
            with open(os.path.join(consts.CONFIG_PATH, fl)) as json_file:
                json_content = json.load(json_file)
                self.collections.append(json_content)

    def load_new_collection(self, new_collection: str):
        json_content = json.loads(new_collection)
        self.collections.append(json_content)

    def get_collections_tree_store(self) -> Gtk.TreeStore:
        model_store = Gtk.TreeStore.new((
            GObject.TYPE_BOOLEAN, # type
            GObject.TYPE_STRING,  # method
            GObject.TYPE_STRING,  # name
            GObject.TYPE_STRING,  # request json string
        ))

        for collection in self.collections:
            root_iter: Gtk.TreeIter = model_store.append(None)
            model_store.set(root_iter, consts.TYPE, consts.TREE_COLLECTION, consts.METHOD, "", consts.NAME, collection["info"]["name"])

            for item in collection["item"]:
                self._recursive_collection_parser(model_store, root_iter, item)
        
        return model_store

    def store_collections_from_tree_store(self, model_store: Gtk.TreeStore):
        pass

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

    def export_collection(self, name):
        pass
