import re
import tkinter as tk
from collections import defaultdict
from tkinter import ttk


class WidgetManager:
    def __init__(self):
        self.by_id = {}
        self.by_widget = {}
        self.by_tag = defaultdict(list)

    def register(self, widget, widget_id=None, tags=None):
        if widget_id:
            self.by_id[widget_id] = widget
            self.by_widget[widget] = widget_id
        if tags:
            for tag in tags:
                self.by_tag[tag].append(widget)

    def get_by_id(self, widget_id):
        return self.by_id.get(widget_id)

    def get_id_by_widget(self, widget):
        return self.by_widget.get(widget)

    def get_by_tag(self, tag):
        return self.by_tag.get(tag, [])

    def update_all(self, tag, **kwargs):
        for widget in self.get_by_tag(tag):
            widget.config(**kwargs)


class I18nWidgetManager(WidgetManager):
    def __init__(self, i18n_map, i18n_function):
        """
        @param i18n_map:
            key: name of the widget
            value: the translation id of the widget
            e.g.
            {
                "open_label": "open", # -> "open" will be used for function _("open") to translate
                "main_menu": ["new", "open", "save"]
            }
        @param i18n_function:
            the function of the i18n translation
        """
        super().__init__()
        self.i18n_map = i18n_map
        self.i18n_function = i18n_function

    def refresh_i18n(self):
        widgets = self.get_by_tag("i18n")
        for widget in widgets:
            widget_id = self.get_id_by_widget(widget)
            text = self.i18n_map.get(widget_id)
            if isinstance(
                widget,
                (
                    tk.Label,
                    ttk.Label,
                    tk.Button,
                    ttk.Button,
                    tk.Checkbutton,
                    ttk.Checkbutton,
                    tk.Radiobutton,
                    ttk.Radiobutton,
                    tk.Message,  # Message do not have ttk version
                    tk.LabelFrame,
                    ttk.LabelFrame,
                ),
            ):
                widget.config(text=self._process(text))
                continue
            if isinstance(widget, tk.Toplevel):
                widget.title(self._process(text))
                continue
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, self._process(text))
                continue
            if isinstance(widget, tk.Menu):
                texts = self.i18n_map.get(widget_id)
                if not isinstance(texts, list):
                    raise ValueError
                for i, item_text in enumerate(texts):
                    if widget.type(i) in ("command", "radiobutton", "checkbutton"):  # "cascade"
                        # cascade type menu is not supported now
                        widget.entryconfig(i, label=self._process(item_text))
                continue

            raise TypeError

    def _process(self, text):
        def repl(match):
            key = match.group(1)
            return str(self.i18n_function(key))

        return re.sub(r"\{(.*?)}", repl, text)
