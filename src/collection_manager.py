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

    def save_collections_to_disk(self, model_store: Gtk.TreeStore):
        pass

    def tree_iter_to_collection(self, root_iter: Gtk.TreeIter):
        pass

    def persist_collection(self, collection: dict):
        collection_id = collection["info"]["_postman_id"]
        with open(f"{collection_id}.json", "w") as outfile:
            json.dump(collection, outfile)