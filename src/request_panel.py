import threading

from gi.repository import Gtk, GtkSource, GObject, Pango, GLib

import logging

from . import constants
from .request_handler import RequestHandler

class RequestPanel(Gtk.Paned):

    def __init__(self, method: str = "GET", url: str = "", body: str = "", headers: list[tuple[str, str]] = None):
        super().__init__()
        self.url_entry_field = None
        self.request_text_buffer = None
        self.send_button = None
        self.response_text_editor = None
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_position(300)

        if body != "":
            self.request_text_buffer = Gtk.EntryBuffer(body, len(body))

        self.headers_store: Gtk.ListStore = Gtk.ListStore.new((GObject.TYPE_STRING, GObject.TYPE_STRING))
        # self.headers_store.append(("Authorization", "Bearer tokenxyz"))

        self.upper_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.upper_box.pack_start(self.create_url_component(url), False, False, 5)
        self.upper_box.pack_start(self.create_notebook(), True, True, 0)

        self.pack1(self.upper_box, True, False)

        self.method = method

        self.response_text_editor = self.create_text_editor()
        self.response_text_buffer: Gtk.EntryBuffer = self.response_text_editor.get_buffer()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.response_text_editor)
        self.pack2(scrolled_window, True, False)

    def create_text_editor(self) -> GtkSource.View:
        text_editor = GtkSource.View.new()
        text_editor.modify_font(Pango.FontDescription('monospace 12'))
        text_editor.set_highlight_current_line(True)
        text_editor.set_auto_indent(True)
        text_editor.set_show_line_numbers(True)
        text_editor.set_wrap_mode(Gtk.WrapMode.WORD)
        text_editor.set_indent_width(constants.DEFAULT_INDENT_WIDTH)

        buffer = text_editor.get_buffer()
        txt = '{"test": true, "id": 123, "name": "someone", "list": [{"test": "123"}]}'
        buffer.set_text(txt)

        lm = GtkSource.LanguageManager.new()
        lang = lm.get_language("json")
        
        buffer.set_highlight_syntax(True)
        buffer.set_language(lang)

        manager = GtkSource.StyleSchemeManager().get_default()
        scheme = manager.get_scheme("builder")
        buffer.set_style_scheme(scheme)

        buffer.set_text(txt, len(txt))

        return text_editor

    def create_url_component(self, url: str) -> Gtk.Widget:
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        method_combo_box = Gtk.ComboBoxText.new()
        method_combo_box.append("get", constants.METHOD_GET)
        method_combo_box.append("post", constants.METHOD_POST)
        method_combo_box.append("put", constants.METHOD_PUT)
        method_combo_box.append("patch", constants.METHOD_PATCH)
        method_combo_box.append("delete", constants.METHOD_DELETE)
        method_combo_box.set_active(0)
        self.method = method_combo_box.get_active_text()
        method_combo_box.connect("changed", self.on_method_combo_box_changed)

        self.url_entry_field = Gtk.Entry()
        self.url_entry_field.set_placeholder_text("URL")
        if url:
            self.url_entry_field.set_text(url)

        self.send_button: Gtk.Button = Gtk.Button.new_with_label("Send")
        self.send_button.connect("clicked", self.on_send_button_clicked)

        box.pack_start(method_combo_box, False, False, constants.DEFAULT_SPACING)
        box.pack_start(self.url_entry_field, True, True, 0)
        box.pack_start(self.send_button, False, False, constants.DEFAULT_SPACING)

        return box

    def create_notebook(self) -> Gtk.Widget:
        notebook = Gtk.Notebook.new()
        notebook.append_page(self.create_headers_page(self.headers_store), Gtk.Label.new("Headers"))

        request_text_editor = self.create_text_editor()
        if self.request_text_buffer is None:
            self.request_text_buffer: Gtk.EntryBuffer = request_text_editor.get_buffer()
        else:
            request_text_editor.set_buffer(self.request_text_buffer)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(request_text_editor)

        notebook.append_page(scrolled_window, Gtk.Label.new("Body"))
        return notebook

    def on_headers_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            logging.debug("headers selection changed: " + model[treeiter][0])

    def create_headers_page(self, store: Gtk.ListStore) -> Gtk.TreeView:
        tree_view = Gtk.TreeView(model=store)
        tree_view.append_column(Gtk.TreeViewColumn("Key", Gtk.CellRendererText(), text=0))
        tree_view.append_column(Gtk.TreeViewColumn("Value", Gtk.CellRendererText(), text=1))

        select = tree_view.get_selection()
        select.connect("changed", self.on_headers_selection_changed)

        return tree_view

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
            self.request_text_buffer.get_text(self.request_text_buffer.get_start_iter(),
                                              self.request_text_buffer.get_end_iter(), False),
            self.get_headers()
        )
        res = rh.send()
        if res is not None:
            body = str(res.content, 'UTF-8')
        else:
            body = ""
        GLib.idle_add(self.perform_request_ui_callback, body)

    def perform_request_ui_callback(self, body: str):
        self.response_text_buffer.set_text(body, len(body))
        self.send_button.set_sensitive(True)
        self.send_button.set_label("Send")

    def on_method_combo_box_changed(self, combo_box: Gtk.ComboBoxText):
        self.method = combo_box.get_active_text()

    def get_headers(self) -> dict[str, str]:
        headers = {}
        for row in self.headers_store:
            headers[row[0]] = row[1]
        
        return headers

