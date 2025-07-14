from tkinter import ttk

from PIL import ImageTk

from src.hexo_helper.core.mvc.view import View
from src.hexo_helper.core.utils.ui import UI
from src.hexo_helper.service.constants import MAIN_INFO_CLICKED, MAIN_SETTINGS_CLICKED
from src.hexo_helper.service.enum import BlackboardKey


class MainView(View):
    def __init__(self):
        super().__init__()
        # PhotoImage objects need to be stored as instance variables to prevent garbage collection.
        self.info_icon = None
        self.settings_icon = None
        # Icons must be instance variables to prevent garbage collection
        self.info_icon = None  # to load
        self.settings_icon = None  # to load
        self.button_size = 32

    def create_widgets(self):
        """
        Creates widgets with categorical tags for granular control:
        - 'container': For layout frames.
        - 'label': For static text labels.
        - 'button': For clickable buttons.
        - 'i18n': A cross-cutting tag for any widget whose text needs translation.
        """
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True)
        UI.center_window(main_frame.winfo_toplevel())
        # The main frame is a container.
        self.widgets.register(main_frame, widget_id="main_frame", tags={"container"})
        self.window = main_frame

        # --- Styles ---
        style = ttk.Style()
        style.configure("Header.TFrame", background="#f0f0f0")
        style.configure("Header.TButton", background="#f0f0f0", borderwidth=0, focuscolor="none")
        style.map("Header.TButton", background=[("active", "#e0e0e0")])

        # --- Custom Title Bar ---
        title_bar = ttk.Frame(main_frame, height=self.button_size + 10, style="Header.TFrame")
        title_bar.pack(fill="x", side="top", padx=1, pady=1)
        title_bar.pack_propagate(False)
        # The title bar is a container.
        self.widgets.register(title_bar, widget_id="title_bar", tags={"container"})

        info_button = ttk.Button(title_bar, style="Header.TButton")
        info_button.pack(side="right", padx=(0, 10))
        self.widgets.register(info_button, widget_id="info_button", tags={"button"})

        settings_button = ttk.Button(title_bar, style="Header.TButton")
        settings_button.pack(side="right", padx=(0, 5))
        self.widgets.register(settings_button, widget_id="settings_button", tags={"button"})

        title_label = ttk.Label(title_bar, text="...", font=("Segoe UI", 16, "bold"), background="#f0f0f0")
        title_label.pack(expand=True)
        # This is a label. Its text is dynamic, so we won't tag it 'i18n' for static translation.
        self.widgets.register(title_label, widget_id="title_label", tags={"label"})

        # --- Main Content Area ---
        main_content_frame = ttk.Frame(main_frame, padding=10)
        main_content_frame.pack(fill="both", expand=True)
        # The content area is a container.
        self.widgets.register(main_content_frame, widget_id="main_content_frame", tags={"container"})

    def init_data(self, model_data: dict) -> None:
        """Initial data fill using the provided model_data dictionary."""
        app_name = model_data.get(BlackboardKey.APP_NAME.value, "")
        title_label = self.widgets.get_by_id("title_label")
        title_label.config(text=app_name)

    def load_images(self, images_data: dict):
        self.settings_icon = ImageTk.PhotoImage(images_data["settings"])
        self.info_icon = ImageTk.PhotoImage(images_data["info"])
        self.widgets.get_by_id("settings_button").config(image=self.settings_icon)
        self.widgets.get_by_id("info_button").config(image=self.info_icon)

    def setup_bindings(self):
        """Set up all event bindings here."""
        settings_button = self.widgets.get_by_id("settings_button")
        settings_button.config(command=lambda: self.producer.send_event(MAIN_SETTINGS_CLICKED))

        info_button = self.widgets.get_by_id("info_button")
        info_button.config(command=lambda: self.producer.send_event(MAIN_INFO_CLICKED))
