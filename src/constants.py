from pathlib import Path
import os

METHOD_GET = "GET"
METHOD_POST = "POST"
METHOD_PUT = "PUT"
METHOD_PATCH = "PATCH"
METHOD_DELETE = "DELETE"

DEFAULT_SPACING = 5
DEFAULT_INDENT_WIDTH = 4
CONFIG_PATH = str(os.path.join(Path.home(), ".config/courier"))
