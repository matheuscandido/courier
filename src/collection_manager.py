from pathlib import Path
import json
import os
import logging
from typing import List

from gi.repository import Gtk, GObject
from .constants import *

class CollectionManager:

    def __init__(self) -> None:
        # Check if coutier dir exists, creates if not
        if not os.path.exists(CONFIG_PATH):
            os.mkdir(CONFIG_PATH)
            logging.debug("config path created")
        else:
            logging.debug("config path already exists")

        # Loads all .json collections listed there
        self.colletions: List[dict] = []

    def load_all_collections(self) -> List[dict]:
        json_files = [f for f in os.listdir(CONFIG_PATH) if f.endswith(".json")]
        for fl in json_files:
            with open(os.path.join(CONFIG_PATH, fl)) as json_file:
                json_content = json.load(json_file)
                self.colletions.append(json_content)
        logging.debug("collections imported: " + str(self.colletions))

    def get_collections_tree_store(self) -> Gtk.TreeStore:
        model_store = Gtk.TreeStore.new((
            GObject.TYPE_BOOLEAN, # type
            GObject.TYPE_STRING,  # method
            GObject.TYPE_STRING,  # name
            GObject.TYPE_STRING,  # request json string
        ))

        for collection in self.colletions:
            root_iter: Gtk.TreeIter = model_store.append(None)
            model_store.set(root_iter, TYPE, TREE_COLLECTION, METHOD, "", NAME, collection["info"]["name"])

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
                    TYPE, TREE_REQUEST,
                    METHOD, item["request"]["method"],
                    NAME, item["name"],
                    REQUEST_JSON_STRING, json.dumps(item))
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
                    self._recursive_collection_parser(
                        model_store=model_store,
                        parent_iter=item_iter,
                        item=child
                    )

    def export_collection(self, name):
        pass
