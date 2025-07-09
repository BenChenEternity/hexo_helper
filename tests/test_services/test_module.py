import tkinter
from unittest.mock import MagicMock

import pytest

import src.hexo_helper.service.services.module as service_module
from src.hexo_helper.common import ModuleRegistryKey
from src.hexo_helper.common.module import Module, create_module_dict


# Define specific mock module classes
class MainModuleMock(Module):
    pass


class SettingsModuleMock(Module):
    pass


class DashboardModuleMock(Module):
    pass


class WidgetModuleMock(Module):
    pass


class UniqueToolMock(Module):
    pass


class NonUniqueToolMock(Module):
    pass


@pytest.fixture
def module_service_fixture(monkeypatch):
    """Sets up a mock environment and a ModuleService instance for testing."""
    # Reset counters for non-unique modules to ensure test isolation
    NonUniqueToolMock.count = 0

    # Define a complex module hierarchy for comprehensive testing
    test_registered_modules = {
        "main": create_module_dict(
            MainModuleMock,
            {
                "settings": create_module_dict(
                    SettingsModuleMock,
                    activate_immediately=False,
                ),
                "dashboard": create_module_dict(
                    DashboardModuleMock,
                    {
                        "widget": create_module_dict(
                            WidgetModuleMock,
                        ),
                        "unique_tool": create_module_dict(
                            UniqueToolMock,
                        ),
                    },
                ),
                "non_unique_tool": create_module_dict(NonUniqueToolMock, is_unique=False),
            },
        )
    }
    monkeypatch.setattr(service_module, "registered_modules", test_registered_modules)

    # Mock the tkinter root window
    mock_root = MagicMock(spec=tkinter.Toplevel)

    # Instantiate the service
    service = service_module.ModuleService(mock_root)
    service.registered_modules = test_registered_modules

    return service


class TestModuleService:
    """A collection of unit tests for the ModuleService class."""

    def test_initialization_and_id_injection(self, module_service_fixture):
        """
        Tests if the service initializes correctly and injects the full path IDs
        into the module classes.
        """
        service = module_service_fixture
        assert service is not None
        assert isinstance(service.activated_tree, MainModuleMock)

        # Verify that IDs were injected correctly into the class attributes
        assert MainModuleMock.id == "main"
        assert SettingsModuleMock.id == "main.settings"
        assert DashboardModuleMock.id == "main.dashboard"
        assert WidgetModuleMock.id == "main.dashboard.widget"
        assert UniqueToolMock.id == "main.dashboard.unique_tool"
        assert NonUniqueToolMock.id == "main.non_unique_tool"

    def test_initial_activated_tree_structure(self, module_service_fixture):
        """
        Tests if the initial tree of activated modules is built correctly,
        respecting the 'activate_immediately' flag.
        """
        service = module_service_fixture

        # main is the root and should always be activated
        main_module = service.activated_tree
        assert isinstance(main_module, MainModuleMock)

        # dashboard was marked 'activate_immediately', so it should be a child
        assert "dashboard" in main_module.children
        dashboard_module = main_module.children["dashboard"]
        assert isinstance(dashboard_module, DashboardModuleMock)

        # widget is a child of dashboard and also marked 'activate_immediately'
        assert "widget" in dashboard_module.children
        assert isinstance(dashboard_module.children["widget"], WidgetModuleMock)

        # settings was not marked 'activate_immediately', so it should NOT be in the tree
        assert "settings" not in main_module.children

    def test_get_registered_module_info(self, module_service_fixture):
        """
        Tests successful retrieval of module metadata from the registration dictionary.
        """
        service = module_service_fixture

        # Test root level
        info = service.get_registered_module_info("main")
        assert info[ModuleRegistryKey.CLASS.value] == MainModuleMock

        # Test nested level
        info = service.get_registered_module_info("main.dashboard")
        assert info[ModuleRegistryKey.CLASS.value] == DashboardModuleMock

        # Test deep nested level
        info = service.get_registered_module_info("main.dashboard.widget")
        assert info[ModuleRegistryKey.CLASS.value] == WidgetModuleMock

    def test_get_registered_module_info_failure(self, module_service_fixture):
        """Tests that getting info for a non-existent module raises a KeyError."""
        service = module_service_fixture
        with pytest.raises(KeyError, match="Module path not found: main.fake"):
            service.get_registered_module_info("main.fake")

        with pytest.raises(KeyError, match="No child modules under: main.dashboard.widget"):
            service.get_registered_module_info("main.dashboard.widget.child")

    def test_get_activated_module(self, module_service_fixture):
        """Tests successful retrieval of already activated module instances."""
        service = module_service_fixture

        main_module = service.get_activated_instance("main")
        assert isinstance(main_module, MainModuleMock)

        dashboard_module = service.get_activated_instance("main.dashboard")
        assert isinstance(dashboard_module, DashboardModuleMock)

        widget_module = service.get_activated_instance("main.dashboard.widget")
        assert isinstance(widget_module, WidgetModuleMock)

    def test_get_activated_module_failure(self, module_service_fixture):
        """
        Tests that getting a non-activated or non-existent module instance
        raises the appropriate errors.
        """
        service = module_service_fixture

        # settings is registered but not activated
        with pytest.raises(KeyError):
            service.get_activated_instance("main.settings")

        # fake does not exist at all
        with pytest.raises(KeyError):
            service.get_activated_instance("main.fake")

        # Root module mismatch
        with pytest.raises(ValueError):
            service.get_activated_instance("fake_root.dashboard")

    def test_activate_unique_module(self, module_service_fixture):
        # TODO 先完善 MVC
        """Tests activating a module marked as unique."""
        service = module_service_fixture

        # Activate the unique tool under the dashboard
        with pytest.raises(RuntimeError):
            service.activate("main.dashboard.unique_tool", "main.dashboard", {"data": 1})

        # Verify it was added to the tree
        activated_tool = service.get_activated_instance("main.dashboard.unique_tool")
        assert isinstance(activated_tool, UniqueToolMock)
        assert activated_tool.model.data == {"data": 1}

        # Activating it again should just replace it under the same name
        instance_name_2 = service.activate("main.dashboard.unique_tool", "main.dashboard", {"data": 2})
        assert instance_name_2 == "unique_tool"

        # The parent should still have only one child with that name
        dashboard = service.get_activated_instance("main.dashboard")
        assert len([c for c in dashboard.children if c.startswith("unique_tool")]) == 1

        # Verify the new instance is now in the tree
        activated_tool_2 = service.get_activated_instance("main.dashboard.unique_tool")
        assert activated_tool_2.model_data == {"data": 2}

    def test_activate_non_unique_module(self, module_service_fixture):
        # TODO 先完善 MVC
        """
        Tests activating a module not marked as unique, which should result
        in numbered instances.
        """
        service = module_service_fixture

        # Activate the first instance
        instance_name_1 = service.activate("main.non_unique_tool", "main", {"id": 1})
        assert instance_name_1 == "non_unique_tool@1"

        # Verify it exists in the tree
        tool1 = service.get_activated_instance("main.non_unique_tool@1")
        assert isinstance(tool1, NonUniqueToolMock)
        assert tool1.model_data == {"id": 1}

        # Activate a second instance
        instance_name_2 = service.activate("main.non_unique_tool", "main", {"id": 2})
        assert instance_name_2 == "non_unique_tool@2"

        # Verify the second one also exists
        tool2 = service.get_activated_instance("main.non_unique_tool@2")
        assert isinstance(tool2, NonUniqueToolMock)
        assert tool2.model_data == {"id": 2}

        # Check that the parent has both children
        main_module = service.get_activated_instance("main")
        assert "non_unique_tool@1" in main_module.children
        assert "non_unique_tool@2" in main_module.children

    def test_activate_module_with_non_activated_parent(self, module_service_fixture):
        """
        Tests that attempting to activate a module under a parent that is not
        currently activated raises a KeyError.
        """
        service = module_service_fixture

        # main.settings is a valid registration path, but it's not an activated module.
        # Therefore, we cannot add a child to it.
        with pytest.raises(KeyError):
            service.activate("main.dashboard.widget", "main.settings", {})
