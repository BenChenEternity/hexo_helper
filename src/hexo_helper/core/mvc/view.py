import tkinter as tk
from abc import abstractmethod
from tkinter import ttk

from src.hexo_helper.core.event import EventBus, Producer


class View:
    def __init__(self) -> None:
        # view ---internal_bus---> controller
        self.producer = None
        self.master = None
        self.widgets = None
        self.window = None

    def set_master(self, master: tk.Toplevel | tk.Tk | tk.Frame | ttk.Frame) -> None:
        self.master = master

    def set_internal_bus(self, internal_bus: EventBus):
        self.producer = Producer(internal_bus)

    @abstractmethod
    def create_widgets(self):
        """
        create widgets here
        """
        pass

    @abstractmethod
    def setup_bindings(self):
        """
        subscribe events
        e.g.: self.my_button.config(command=lambda: self._on_my_button_clicked())
        """
        pass

    @abstractmethod
    def init_data(self, model_data: dict) -> None:
        """Initial data fill"""
        pass

    def update_data(self, model_data: dict) -> None:
        """Update UI with new data (optional)"""
        pass

    def cleanup(self) -> None:
        """destroy widgets, etc."""
        pass

    def get_window(self):
        return self.window.winfo_toplevel() if self.window else None
