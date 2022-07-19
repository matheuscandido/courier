from pathlib import Path
import json
import os
from typing import List

from gi.repository import Gtk, GObject
from . import constants as consts

class CollectionManager:

    def __init__(self) -> None:
        if not os.path.exists(consts.CONFIG_PATH):
            os.mkdir(consts.CONFIG_PATH)

    def load_collections_from_disk(self) -> List[dict]:
        collections: List[dict] = []
        json_files = [f for f in os.listdir(consts.CONFIG_PATH) if f.endswith(".json")]
        for fl in json_files:
            with open(os.path.join(consts.CONFIG_PATH, fl)) as json_file:
                json_content = json.load(json_file)
                collections.append(json_content)

        return collections

    def load_collection(self, content: str) -> dict:
        return json.loads(content)

    def save_model_store_to_disk(self, model_store: Gtk.TreeStore):
        collections = []
        first_iter = model_store.get_iter_first()
        collections.append(self._handle_collection_root_iter(tree_store=model_store, root_iter=first_iter))

        next_iter = model_store.iter_next(first_iter)
        while  next_iter is not None:
            collections.append(self._handle_collection_root_iter(model_store, next_iter))
            next_iter = model_store.iter_next(next_iter)

        for collection in collections:
            self._persist_collection_dict_to_disk(collection)

    def _handle_collection_root_iter(self, tree_store: Gtk.TreeStore, root_iter: Gtk.TreeIter) -> dict:
        collection = {}
        (info,) = tree_store.get(root_iter, consts.INFO)
        collection["info"] = json.loads(info)
        collection["item"] = []
        
        self._recursive_handle_collection_iter(tree_store, root_iter, collection["item"])
        return collection


    def _recursive_handle_collection_iter(self, tree_store: Gtk.TreeStore, parent_iter: Gtk.TreeIter, items: list):
        next_iter = tree_store.iter_next(parent_iter)
        if next_iter is None:
            return

        (iter_type, name, request_json_string) = tree_store.get(next_iter,
            consts.TYPE,
            consts.NAME,
            consts.REQUEST_JSON_STRING
        )

        if iter_type == consts.TREE_REQUEST:
            request_json_dict = json.loads(request_json_string)
            items.append({
                "name": name,
                "request": request_json_dict
            })
            return
        else:
            new_subfolder = {
                "name": name,
                "item": []
            }
            items.append(new_subfolder)
            return self._recursive_handle_collection_iter(tree_store, next_iter, new_subfolder["item"])

    def _persist_collection_dict_to_disk(self, collection_dict: dict):
        print("generated: " + str(collection_dict))

    def persist_collection(self, collection: dict):
        collection_id = collection["info"]["_postman_id"]
        with open(f"{collection_id}.json", "w") as outfile:
            json.dump(collection, outfile)