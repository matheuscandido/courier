from pathlib import Path
import os

METHOD_GET = "get"
METHOD_POST = "post"
METHOD_PUT = "put"
METHOD_PATCH = "patch"
METHOD_DELETE = "delete"

DEFAULT_SPACING = 5
DEFAULT_INDENT_WIDTH = 4
CONFIG_PATH = str(os.path.join(Path.home(), ".config/courier"))

TYPE = 0
INFO = 1
METHOD = 2
NAME = 3
REQUEST_JSON_STRING = 4

TREE_COLLECTION = 0
TREE_REQUEST = 1

METHOD_COLORS = {
    "GET": "#22FF00",
    "POST": "#FFEE00",
    "PUT": "#0055FF",
    "PATCH": "#000000",
    "DELETE": "#FF0000"
}