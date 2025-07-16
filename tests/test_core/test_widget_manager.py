import tkinter as tk
from tkinter import ttk

import pytest

from src.hexo_helper.core.widget import I18nWidgetManager, WidgetManager


class TestWidgetManager:
    """Unit test suite for the WidgetManager class."""

    @pytest.fixture
    def manager(self):
        """Provides a fresh WidgetManager instance for each test."""
        return WidgetManager()

    def test_initialization(self, manager):
        """Test that the manager initializes with empty dictionaries."""
        assert manager.by_id == {}
        assert manager.by_widget == {}
        assert list(manager.by_tag.keys()) == []

    def test_register_and_get(self, manager, mocker):
        """Test registration and retrieval by ID, widget, and tag."""
        mock_widget_1 = mocker.Mock()
        mock_widget_2 = mocker.Mock()

        # Register with ID and tags
        manager.register(mock_widget_1, widget_id="label1", tags=["ui", "text"])
        # Register with only tags
        manager.register(mock_widget_2, tags=["ui", "button"])

        # Test getters
        assert manager.get_by_id("label1") == mock_widget_1
        assert manager.get_id_by_widget(mock_widget_1) == "label1"
        assert manager.get_by_id("non-existent") is None

        # Test tag retrieval
        ui_widgets = manager.get_by_tag("ui")
        assert mock_widget_1 in ui_widgets
        assert mock_widget_2 in ui_widgets
        assert len(ui_widgets) == 2

        text_widgets = manager.get_by_tag("text")
        assert mock_widget_1 in text_widgets
        assert len(text_widgets) == 1

    def test_update_all(self, manager, mocker):
        """Test updating all widgets with a specific tag."""
        w1 = mocker.Mock()
        w2 = mocker.Mock()
        w3 = mocker.Mock()

        manager.register(w1, tags=["updatable"])
        manager.register(w2, tags=["other"])
        manager.register(w3, tags=["updatable"])

        # Update all widgets with the 'updatable' tag
        manager.update_all("updatable", state="disabled", text="Updated")

        # Verify config was called on the correct widgets with the correct arguments
        w1.config.assert_called_once_with(state="disabled", text="Updated")
        w3.config.assert_called_once_with(state="disabled", text="Updated")

        # Verify the widget without the tag was not updated
        w2.config.assert_not_called()


class TestI18nWidgetManager:
    """Unit test suite for the I18nWidgetManager class."""

    @pytest.fixture
    def i18n_manager(self):
        """Provides a manager with a sample map and translation function."""
        i18n_map = {
            "title_label": "{app_title}",
            "save_button": "{actions.save}",
            "main_window": "My App",  # No placeholder
            "file_menu": ["{menu.new}", "{menu.open}"],
            "entry_box": "{placeholders.enter_name}",
        }

        # The mock translation function simply prepends "t_" to the key
        def i18n_function(key):
            return f"t_{key}"

        return I18nWidgetManager(i18n_map, i18n_function)

    def test_process_method(self, i18n_manager):
        """Test the internal _process method for string substitution."""
        # Test a string with one placeholder
        processed_text = i18n_manager._process("{app_title}")
        assert processed_text == "t_app_title"

        # Test a string with no placeholders
        processed_text = i18n_manager._process("Just a regular string")
        assert processed_text == "Just a regular string"

        # Test a more complex string
        processed_text = i18n_manager._process("Action: {actions.save}")
        assert processed_text == "Action: t_actions.save"

    def test_refresh_for_label_and_button(self, i18n_manager, mocker):
        """Test refreshing text for standard widgets like Label and Button."""
        # Create a mock that identifies as a ttk.Label
        mock_label = mocker.create_autospec(ttk.Label)

        # Register the widget with an ID from the map and the 'i18n' tag
        i18n_manager.register(mock_label, widget_id="title_label", tags=["i18n"])

        # Run the refresh
        i18n_manager.refresh_i18n()

        # Verify the widget's config method was called with the translated text
        mock_label.config.assert_called_once_with(text="t_app_title")

    def test_refresh_for_toplevel_window(self, i18n_manager, mocker):
        """Test refreshing the title for a Toplevel window."""
        mock_window = mocker.create_autospec(tk.Toplevel)
        i18n_manager.register(mock_window, widget_id="main_window", tags=["i18n"])

        i18n_manager.refresh_i18n()

        # For windows, it should call .title()
        mock_window.title.assert_called_once_with("My App")

    def test_refresh_for_entry(self, i18n_manager, mocker):
        """Test refreshing the content for an Entry widget."""
        mock_entry = mocker.create_autospec(tk.Entry)
        i18n_manager.register(mock_entry, widget_id="entry_box", tags=["i18n"])

        i18n_manager.refresh_i18n()

        # For Entry, it should first delete existing content, then insert new
        mock_entry.delete.assert_called_once_with(0, tk.END)
        mock_entry.insert.assert_called_once_with(0, "t_placeholders.enter_name")

    def test_refresh_for_menu(self, i18n_manager, mocker):
        """Test refreshing item labels for a Menu widget."""
        mock_menu = mocker.create_autospec(tk.Menu)
        # Configure the mock's .type() method to return 'command' for any index
        mock_menu.type.return_value = "command"

        i18n_manager.register(mock_menu, widget_id="file_menu", tags=["i18n"])

        i18n_manager.refresh_i18n()

        # Verify entry config was called for each item in the menu list
        expected_calls = [
            mocker.call(0, label="t_menu.new"),
            mocker.call(1, label="t_menu.open"),
        ]
        mock_menu.entryconfig.assert_has_calls(expected_calls, any_order=False)
        assert mock_menu.entryconfig.call_count == 2

    def test_refresh_raises_type_error_for_unsupported_widget(self, i18n_manager, mocker):
        """Test that an unsupported widget type raises a TypeError."""
        # tk.Canvas is not in the list of supported types in refresh_i18n
        mock_canvas = mocker.create_autospec(tk.Canvas)
        i18n_manager.register(mock_canvas, widget_id="some_id", tags=["i18n"])

        with pytest.raises(TypeError):
            i18n_manager.refresh_i18n()

    def test_refresh_raises_value_error_for_bad_menu_map(self, i18n_manager, mocker):
        """Test that a non-list value for a menu in the i18n_map raises a ValueError."""
        mock_menu = mocker.create_autospec(tk.Menu)
        # The map for "save_button" is a string, not a list, which is incorrect for a Menu
        i18n_manager.register(mock_menu, widget_id="save_button", tags=["i18n"])

        with pytest.raises(ValueError):
            i18n_manager.refresh_i18n()
