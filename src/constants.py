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
