import threading

from gi.repository import Gtk, GtkSource, GObject, Pango, GLib

import logging, json

from . import constants as consts
from .request_handler import RequestHandler

HEADERS_KEY = 0
HEADERS_VALUE = 1

@Gtk.Template(resource_path='/com/mcandido/Courier/ui/request_panel.ui')
class RequestPanel(Gtk.Paned):
    __gtype_name__ = 'RequestPanel'

    def __init__(self, method: str = "GET", url: str = "", body: str = "", headers: list[tuple[str, str]] = None, tree_store: Gtk.TreeStore = None, tree_iter: Gtk.TreeIter = None):
        from .request_handler import RequestHandler
        from .tab_panel import TabPanel, TabHandle
        super().__init__()
        self.url_entry_field = None
        self.request_text_buffer = None
        self.send_button = None
        self.save_button = None
        self.response_text_editor = None
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_position(300)
        self.method_combo_box = None

        self.tab_handle: TabHandle = None
        self.notebook: TabPanel =None
        self.tree_store = tree_store
        self.tree_iter = tree_iter

        if body != "":
            self.request_text_buffer = self.create_gtk_source_view_buffer()
            self.request_text_buffer.set_text(body, len(body))

        self.headers_store: Gtk.ListStore = Gtk.ListStore.new((GObject.TYPE_STRING, GObject.TYPE_STRING))
        if headers is not None:
            for header in headers:
                iterator = self.headers_store.append(None)
                self.headers_store.set(iterator, HEADERS_KEY, header[0], HEADERS_VALUE, header[1])

        self.upper_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.upper_box.pack_start(self.create_url_component(url), False, False, 5)
        self.upper_box.pack_start(self.create_notebook(), True, True, 0)

        self.method_combo_box.set_active(self.get_method_number(method))

        self.pack1(self.upper_box, True, False)

        self.method = method

        self.response_text_editor = self.create_text_editor()
        self.response_text_buffer: GtkSource.Buffer = self.response_text_editor.get_buffer()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.response_text_editor)
        self.pack2(scrolled_window, True, False)

    def create_text_editor(self) -> GtkSource.View:
        text_editor = GtkSource.View.new_with_buffer(self.create_gtk_source_view_buffer())
        text_editor.modify_font(Pango.FontDescription('monospace 12'))
        text_editor.set_highlight_current_line(True)
        text_editor.set_auto_indent(True)
        text_editor.set_show_line_numbers(True)
        text_editor.set_wrap_mode(Gtk.WrapMode.WORD)
        text_editor.set_indent_width(consts.DEFAULT_INDENT_WIDTH)

        return text_editor

    def create_gtk_source_view_buffer(self) -> GtkSource.Buffer:
        buffer = GtkSource.Buffer()

        lm = GtkSource.LanguageManager.new()
        lang = lm.get_language("json")

        buffer.set_highlight_syntax(True)
        buffer.set_language(lang)

        manager = GtkSource.StyleSchemeManager().get_default()
        scheme = manager.get_scheme("solarized-dark")
        buffer.set_style_scheme(scheme)

        return buffer

    def create_url_component(self, url: str) -> Gtk.Widget:
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.method_combo_box = Gtk.ComboBoxText.new()
        self.method_combo_box.append(consts.METHOD_GET, consts.METHOD_GET.upper())
        self.method_combo_box.append(consts.METHOD_POST, consts.METHOD_POST.upper())
        self.method_combo_box.append(consts.METHOD_PUT, consts.METHOD_PUT.upper())
        self.method_combo_box.append(consts.METHOD_PATCH, consts.METHOD_PATCH.upper())
        self.method_combo_box.append(consts.METHOD_DELETE, consts.METHOD_DELETE.upper())
        self.method_combo_box.connect("changed", self.on_method_combo_box_changed)

        self.url_entry_field = Gtk.Entry()
        self.url_entry_field.set_placeholder_text("URL")
        if url:
            self.url_entry_field.set_text(url)

        self.send_button: Gtk.Button = Gtk.Button.new_with_label("Send")
        self.send_button.connect("clicked", self.on_send_button_clicked)

        self.save_button: Gtk.Button = Gtk.Button.new_with_label("Save")
        self.save_button.connect("clicked", self.on_save_button_clicked)

        box.pack_start(self.method_combo_box, False, False, consts.DEFAULT_SPACING)
        box.pack_start(self.url_entry_field, True, True, 0)
        box.pack_start(self.send_button, False, False, consts.DEFAULT_SPACING)
        box.pack_start(Gtk.Separator.new(Gtk.Orientation.VERTICAL), False, False, consts.DEFAULT_SPACING)
        box.pack_start(self.save_button, False, False, consts.DEFAULT_SPACING)

        return box

    def create_notebook(self) -> Gtk.Widget:
        notebook = Gtk.Notebook.new()       

        request_text_editor = self.create_text_editor()
        if self.request_text_buffer is None:
            self.request_text_buffer: GtkSource.Buffer = request_text_editor.get_buffer()
        else:
            request_text_editor.set_buffer(self.request_text_buffer)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(request_text_editor)

        notebook.append_page(scrolled_window, Gtk.Label.new("Body"))

        notebook.append_page(self.create_headers_page(self.headers_store), Gtk.Label.new("Headers"))
        return notebook

    def on_headers_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("headers selection changed: " + model[treeiter][0])

    def create_headers_page(self, store: Gtk.ListStore) -> Gtk.VBox:
        vbox = Gtk.VBox.new(False, 0)

        hbox = Gtk.HBox.new(False, 0)
        add_button = Gtk.Button.new_with_label("Add Header")
        add_button.connect("clicked", self.on_add_header_button_clicked, store)
        hbox.pack_end(add_button, expand=False, fill=False, padding=consts.DEFAULT_SPACING)

        vbox.pack_start(hbox, expand=False, fill=False, padding=consts.DEFAULT_SPACING)

        tree_view = Gtk.TreeView(model=store)

        key_renderer = Gtk.CellRendererText.new()
        key_renderer.set_property("editable", True)
        key_renderer.connect("edited", self.cell_edited, tree_view, 0)

        key_column = Gtk.TreeViewColumn("Key", key_renderer, text=0)
        key_column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        key_column.set_min_width(300)
        key_column.set_resizable(True)
        key_column.set_reorderable(True)
        tree_view.append_column(key_column)

        value_renderer = Gtk.CellRendererText.new()
        value_renderer.set_property("editable", True)
        value_renderer.connect("edited", self.cell_edited, tree_view, 1)

        value_column = Gtk.TreeViewColumn("Value", value_renderer, text=1)
        key_column.set_min_width(300)
        value_column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        value_column.set_resizable(True)
        value_column.set_reorderable(True)
        tree_view.append_column(value_column)

        select = tree_view.get_selection()
        select.connect("changed", self.on_headers_selection_changed)

        vbox.pack_end(tree_view, expand=True, fill=True, padding=consts.DEFAULT_SPACING)

        return vbox

    def on_add_header_button_clicked(self, button: Gtk.Button, store: Gtk.ListStore):
        iter = store.append()
        store.set(iter, HEADERS_KEY, "new key...", HEADERS_VALUE, "new value...")

    def cell_edited(self, renderer, path, new_text, treeview, index):
        if len(new_text) > 0:
            model = treeview.get_model()
            iter = model.get_iter_from_string(path)
            if iter:
                model.set(iter, index, new_text)

    def get_method_number(self, method: str) -> int:
        methods_list = (
            consts.METHOD_GET.upper(),
            consts.METHOD_POST.upper(),
            consts.METHOD_PUT.upper(),
            consts.METHOD_PATCH.upper(),
            consts.METHOD_DELETE.upper())

        for index, m in enumerate(methods_list):
            if method == m:
                return index

        return 0

    def set_tab_handle_ref(self, tab_handle):
        self.tab_handle = tab_handle

    def set_notebook_ref(self, notebook):
        self.notebook = notebook

    def _get_request_body_text(self) -> str:
        return self.request_text_buffer.get_text(self.request_text_buffer.get_start_iter(),
            self.request_text_buffer.get_end_iter(), 
            False)

    def _update_iter_data(self):
        (request_json_string_before,) = self.tree_store.get(self.tree_iter, consts.REQUEST_JSON_STRING)
        request_json_dict = json.loads(request_json_string_before)
        
        if "body" in request_json_dict:
            request_json_dict["request"]["body"]["raw"] = self._get_request_body_text()
        else:
            request_json_dict["request"]["body"] = {
                "raw": self._get_request_body_text()
            }
        
        request_json_dict["request"]["url"]["raw"] = self.url_entry_field.get_text()

        request_json_str = json.dumps(request_json_dict)

        Gtk.TreeStore.set(self.tree_store, self.tree_iter, 
            consts.TYPE, consts.TREE_REQUEST,
            consts.METHOD, self.method,
            consts.NAME, self.tab_handle.get_name(),
            consts.REQUEST_JSON_STRING, request_json_str)


    ###########
    # SIGNALS #
    ###########

    def on_send_button_clicked(self, button: Gtk.Button):
        button.set_sensitive(False)
        button.set_label("Sending")

        self.response_text_editor.set_sensitive(False)
        sending_req_text = "Sending request..."
        self.response_text_buffer.set_text(sending_req_text, len(sending_req_text))

        thread = threading.Thread(target=self.perform_request)
        thread.daemon = True
        thread.start()

    def perform_request(self):
        rh = RequestHandler(
            self.method,
            self.url_entry_field.get_text(),
            self._get_request_body_text(),
            self.get_headers()
        )
        res = rh.send()
        if res is not None:
            body = json.dumps(json.loads(str(res.content, 'UTF-8')), indent=4, sort_keys=True)
        else:
            body = ""
        GLib.idle_add(self.perform_request_ui_callback, body)

    def perform_request_ui_callback(self, body: str):
        self.response_text_buffer.set_text(body, len(body))
        self.response_text_editor.set_sensitive(True)
        self.send_button.set_sensitive(True)
        self.send_button.set_label("Send")

    def on_method_combo_box_changed(self, combo_box: Gtk.ComboBoxText):
        self.method = combo_box.get_active_text()


    def get_headers(self) -> dict[str, str]:
        headers = {}
        for row in self.headers_store:
            headers[row[0]] = row[1]
        
        return headers

    def on_save_button_clicked(self, button: Gtk.Button):
        self._update_iter_data()
