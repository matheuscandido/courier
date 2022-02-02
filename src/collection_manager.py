from pathlib import Path
import json
import os
import logging
from typing import List

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


    def export_collection(self, name):
        pass
