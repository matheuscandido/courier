from gi.repository import Gtk, GObject

from . import constants

METHOD = 0
NAME = 1

JSON_REQUESTS = (
    ("GET", "Get Item"),
    ("POST", "Create Item"),
    ("PUT", "Change Item"),
    ("PATCH", "Amend Item"),
    ("DELETE", "Delete Item")
)

class Sidebar(Gtk.ScrolledWindow):

    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.tree_view = Gtk.TreeView.new()
        self.setup_tree_view()

        tree_view_store = Gtk.ListStore.new((GObject.TYPE_STRING, GObject.TYPE_STRING))
        for row in JSON_REQUESTS:
            iter = tree_view_store.append(None)
            tree_view_store.set(iter, METHOD, row[METHOD], NAME, row[NAME])

        self.tree_view.set_model(tree_view_store)

        self.add(self.tree_view)
    
    def setup_tree_view(self):
        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Method", renderer, text=METHOD)
        self.tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn("Name", renderer, text=NAME)
        self.tree_view.append_column(column)
