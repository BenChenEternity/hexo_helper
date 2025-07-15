import tkinter as tk
from enum import Enum
from tkinter import ttk
from typing import Set

from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.core.utils.ui import UI
from src.hexo_helper.core.widget import I18nWidgetManager
from src.hexo_helper.exceptions import WidgetNotFoundException
from src.hexo_helper.service.constants import (
    CLOSE_WINDOW_CLICKED,
    MAIN_SETTINGS_APPLY_CLICKED,
    MAIN_SETTINGS_LANGUAGE_SELECTED,
)
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.settings import LANGUAGES

from . import _


class I18nWidgetsId(Enum):
    TOPLEVEL_WINDOW = "toplevel_window"
    LANGUAGE_FRAME = "language_frame"
    LANGUAGE_LABEL = "language_label"
    APPLY_BUTTON = "apply_button"


class SettingsView(View):
    def __init__(self):
        super().__init__()
        self.lang_var = tk.StringVar()

    def create_widgets(self):
        """
        Creates widgets with categorical tags for granular control:
        - 'container': For layout frames.
        - 'label': For static text labels.
        - 'button': For clickable buttons.
        - 'input': For user input fields like Combobox, Entry, etc.
        - 'dirty_indicator': For labels that show a state (*), not translatable text.
        - 'i18n': A cross-cutting tag for any widget whose text needs translation.
        """
        i18n_map = {
            I18nWidgetsId.TOPLEVEL_WINDOW.value: "{Settings}",
            I18nWidgetsId.LANGUAGE_FRAME.value: "{Language Settings}",
            I18nWidgetsId.LANGUAGE_LABEL.value: "{Language}:",
            I18nWidgetsId.APPLY_BUTTON.value: "{Apply}",
        }
        self.widgets = I18nWidgetManager(i18n_map, _)

        toplevel_window = tk.Toplevel(self.master.winfo_toplevel())
        UI.center_window(toplevel_window)
        # The window is a container, and its title is translatable.
        self.widgets.register(
            toplevel_window, widget_id=I18nWidgetsId.TOPLEVEL_WINDOW.value, tags=["container", "i18n"]
        )
        self.window = toplevel_window

        main_frame = ttk.Frame(toplevel_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.widgets.register(main_frame, tags=["container"])

        # --- Language Settings ---
        language_frame = ttk.LabelFrame(main_frame, padding=10)
        language_frame.pack(fill="x")
        language_frame.grid_columnconfigure(0, minsize=120)
        language_frame.grid_columnconfigure(1, weight=1)
        # This is a container and its text is translatable.
        self.widgets.register(language_frame, widget_id="language_frame", tags=["container", "i18n"])

        language_label_frame = ttk.Frame(language_frame)
        language_label_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.widgets.register(language_label_frame, tags=["container"])

        language_label = ttk.Label(language_label_frame, text=_("Language") + ":")
        language_label.pack(side="left")
        # This is a text label and is translatable.
        self.widgets.register(language_label, widget_id="language_label", tags=["label", "i18n"])

        language_label_star = ttk.Label(language_label_frame, text="", foreground="red")
        language_label_star.pack(side="left")
        # This has the specific function of being a dirty indicator.
        self.widgets.register(language_label_star, widget_id="language_label_star", tags=["dirty_indicator"])

        lang_combo = ttk.Combobox(
            language_frame,
            textvariable=self.lang_var,
            values=list(LANGUAGES.values()),
            state="readonly",
            justify="center",
        )
        lang_combo.grid(row=0, column=1, sticky="we")
        # This is a user input widget.
        self.widgets.register(lang_combo, widget_id="lang_combo", tags=["input"])

        # --- Apply Button ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        self.widgets.register(button_frame, tags=["container"])

        apply_button = ttk.Button(button_frame, text=_("Apply"))
        apply_button.pack(side="right")
        apply_button.config(state="disabled")
        # This is a button and is translatable.
        self.widgets.register(apply_button, widget_id="apply_button", tags=["button", "i18n"])

        self.widgets.refresh_i18n()

    def cleanup(self) -> None:
        toplevel_window = self.widgets.get_by_id("toplevel_window")
        toplevel_window.destroy()

    def setup_bindings(self):
        """Set up all event bindings here."""
        toplevel_window = self.widgets.get_by_id("toplevel_window")
        toplevel_window.protocol("WM_DELETE_WINDOW", lambda: self.producer.send_event(CLOSE_WINDOW_CLICKED))

        lang_combo = self.widgets.get_by_id("lang_combo")
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_selected)

        apply_button = self.widgets.get_by_id("apply_button")
        apply_button.config(command=lambda: self.producer.send_event(MAIN_SETTINGS_APPLY_CLICKED))

    def init_data(self, model_data: dict) -> None:
        """Initial data fill using the provided model_data dictionary."""
        lang_code = model_data.get(BlackboardKey.LANGUAGE.value)
        lang_display_name = LANGUAGES.get(lang_code, "English")
        self.lang_var.set(lang_display_name)

    def _on_language_selected(self, event):
        """Handle language selection from the combobox."""
        selected_language_name = event.widget.get()
        lang_map = {v: k for k, v in LANGUAGES.items()}
        lang_code = lang_map.get(selected_language_name)
        if lang_code and self.producer:
            self.producer.send_event(MAIN_SETTINGS_LANGUAGE_SELECTED, lang_code=lang_code)

    def mark_dirty(self, labels: Set) -> None:
        for label in labels:
            widget = self.widgets.get_by_id(f"{label}_label_star")
            if widget is None:
                raise WidgetNotFoundException
            widget.config(text="*")
        self.widgets.get_by_id("apply_button").config(state="normal")

    def clear_dirty(self):
        indicators: list = self.widgets.get_by_tag("dirty_indicator")
        for indicator in indicators:
            indicator.config(text="")
        self.widgets.get_by_id("apply_button").config(state="disabled")

    def refresh_i18n(self):
        self.widgets.refresh_i18n()
        # # Update window title
        # toplevel_window = self.widgets.get_by_id("toplevel_window")
        # toplevel_window.title(_("Settings"))
        #
        # # Update labelframe text
        # language_frame = self.widgets.get_by_id("language_frame")
        # language_frame.config(text=_("Language Settings"))
        #
        # # Update label text
        # language_label = self.widgets.get_by_id("language_label")
        # language_label.config(text=_("Language") + ":")
        #
        # # Update button text
        # apply_button = self.widgets.get_by_id("apply_button")
        # apply_button.config(text=_("Apply"))
