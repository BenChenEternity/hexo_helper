import tkinter as tk
from enum import Enum
from tkinter import ttk
from typing import Set

from PIL import ImageTk

from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.core.utils.ui import UI
from src.hexo_helper.core.widget import I18nWidgetManager
from src.hexo_helper.exceptions import WidgetNotFoundException
from src.hexo_helper.service.constants import (
    CLOSE_WINDOW_CLICKED,
    MAIN_SETTINGS_APPLY_CLICKED,
    MAIN_SETTINGS_LANGUAGE_SELECTED,
    MAIN_SETTINGS_THEME_SELECTED,
)
from src.hexo_helper.service.enum import BlackboardKey
from src.hexo_helper.settings import DEFAULT_SETTINGS, LANGUAGES, THEMES

from . import _


class I18nWidgetsId(Enum):
    TOPLEVEL_WINDOW = "toplevel_window"
    LANGUAGE_FRAME = "language_frame"
    LANGUAGE_LABEL = "language_label"
    THEME_FRAME = "theme_frame"
    THEME_LABEL = "theme_label"
    APPLY_BUTTON = "apply_button"


class SettingsView(View):
    def __init__(self):
        super().__init__()
        self.lang_var = tk.StringVar()
        self.theme_var = tk.StringVar()

        self.settings_icon = None
        # which dirty indicator is to change
        self.dirty_indicator_map = {
            BlackboardKey.LANGUAGE.value: "language_label_star",
            BlackboardKey.THEME.value: "theme_label_star",
        }

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
            I18nWidgetsId.THEME_FRAME.value: "{Theme Settings}",
            I18nWidgetsId.THEME_LABEL.value: "{Theme}:",
            I18nWidgetsId.APPLY_BUTTON.value: "{Apply}",
        }
        self.widgets = I18nWidgetManager(i18n_map, _)

        toplevel_window = tk.Toplevel(self.master.winfo_toplevel())
        toplevel_window.title(_("Settings"))
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
        language_frame = ttk.LabelFrame(main_frame, text=_("Language Settings"), padding=10)
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

        # --- Theme Settings ---
        theme_frame = ttk.LabelFrame(main_frame, text=_("Theme Settings"), padding=10)
        theme_frame.pack(fill="x", pady=(10, 0))
        theme_frame.grid_columnconfigure(0, minsize=120)
        theme_frame.grid_columnconfigure(1, weight=1)
        self.widgets.register(theme_frame, widget_id="theme_frame", tags=["container", "i18n"])

        theme_label_frame = ttk.Frame(theme_frame)
        theme_label_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.widgets.register(theme_label_frame, tags=["container"])

        theme_label = ttk.Label(theme_label_frame, text=_("Theme") + ":")
        theme_label.pack(side="left")
        self.widgets.register(theme_label, widget_id="theme_label", tags=["label", "i18n"])

        theme_label_star = ttk.Label(theme_label_frame, text="", foreground="red")
        theme_label_star.pack(side="left")
        self.widgets.register(theme_label_star, widget_id="theme_label_star", tags=["dirty_indicator"])

        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=list(THEMES.values()),
            state="readonly",
            justify="center",
        )
        theme_combo.grid(row=0, column=1, sticky="we")
        self.widgets.register(theme_combo, widget_id="theme_combo", tags=["input"])

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

        theme_combo = self.widgets.get_by_id("theme_combo")
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_selected)

        apply_button = self.widgets.get_by_id("apply_button")
        apply_button.config(command=lambda: self.producer.send_event(MAIN_SETTINGS_APPLY_CLICKED))

    def init_data(self, model_data: dict) -> None:
        """Initial data fill using the provided model_data dictionary."""
        lang_code = model_data.get(BlackboardKey.LANGUAGE.value)
        lang_display_name = LANGUAGES.get(lang_code, DEFAULT_SETTINGS.get(BlackboardKey.LANGUAGE.value))
        theme_code = model_data.get(BlackboardKey.THEME.value)
        theme_display_name = THEMES.get(theme_code, DEFAULT_SETTINGS.get(BlackboardKey.THEME.value))
        self.lang_var.set(lang_display_name)
        self.theme_var.set(theme_display_name)

    def _on_language_selected(self, event):
        """Handle language selection from the combobox."""
        selected_language_name = event.widget.get()
        lang_map = {v: k for k, v in LANGUAGES.items()}
        lang_code = lang_map.get(selected_language_name)
        if lang_code and self.producer:
            self.producer.send_event(MAIN_SETTINGS_LANGUAGE_SELECTED, lang_code=lang_code)

    def _on_theme_selected(self, event):
        """Handle theme selection from the combobox."""
        selected_theme_name = event.widget.get()
        theme_map = {v: k for k, v in THEMES.items()}
        theme_code = theme_map.get(selected_theme_name)
        if theme_code and self.producer:
            self.producer.send_event(MAIN_SETTINGS_THEME_SELECTED, theme_code=theme_code)

    def load_images(self, images_data: dict):
        self.settings_icon = ImageTk.PhotoImage(images_data["settings"])
        toplevel_window = self.widgets.get_by_id("toplevel_window")
        toplevel_window.iconphoto(False, self.settings_icon)

    def mark_dirty(self, labels: Set) -> None:
        for field_name in labels:
            widget_id = self.dirty_indicator_map.get(field_name)
            if not widget_id:
                continue

            widget = self.widgets.get_by_id(widget_id)
            if widget is None:
                raise WidgetNotFoundException(f"Widget with ID '{widget_id}' not found for field '{field_name}'")
            widget.config(text="*")

        apply_button = self.widgets.get_by_id(I18nWidgetsId.APPLY_BUTTON.value)
        if apply_button:
            apply_button.config(state="normal")

    def clear_dirty(self):
        indicators: list = self.widgets.get_by_tag("dirty_indicator")
        for indicator in indicators:
            indicator.config(text="")
        self.widgets.get_by_id("apply_button").config(state="disabled")

    def refresh_i18n(self):
        self.widgets.refresh_i18n()
