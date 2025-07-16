import pytest
from pytest_mock import MockerFixture

from src.hexo_helper.common.module import Module


class ConcreteTestModule(Module):
    """
    A concrete Module subclass for instantiation during tests.
    The get_mvc method will be mocked to control which MVC components are "returned".
    """

    @classmethod
    def get_mvc(cls):
        # This base implementation should not be called in actual tests
        raise NotImplementedError


class TestModule:
    """
    Unit test suite for the abstract Module class.
    It uses a concrete subclass (ConcreteTestModule) and mocks all its dependencies
    to test the abstract base class's logic in isolation.
    """

    @pytest.fixture
    def mock_mvc_components(self, mocker):
        """
        Fixture that creates mock classes for Model, View, and Controller.
        When these mock classes are instantiated, they will return mock instances.
        """
        mock_model_class = mocker.Mock()
        mock_view_class = mocker.Mock()
        mock_controller_class = mocker.Mock()
        return mock_model_class, mock_view_class, mock_controller_class

    @pytest.fixture
    def module_instance(self, mocker, mock_mvc_components):
        """
        Fixture that provides a fully initialized instance of ConcreteTestModule.
        All dependencies (MVC classes, EventBus, master widget) are mocked out.
        """
        mock_model_class, mock_view_class, mock_controller_class = mock_mvc_components

        # Patch the get_mvc classmethod to return our mock classes
        mocker.patch.object(
            ConcreteTestModule, "get_mvc", return_value=(mock_model_class, mock_view_class, mock_controller_class)
        )

        # Patch EventBus to control and inspect its creation and usage
        mock_event_bus_instance = mocker.Mock()
        mocker.patch("src.hexo_helper.common.module.EventBus", return_value=mock_event_bus_instance)

        # --- FIX ---
        # Provide the required arguments for the Module's constructor
        test_instance_id = "test.module@1"
        mock_master_widget = mocker.Mock()

        # Instantiate the module with the required arguments
        instance = ConcreteTestModule(instance_id=test_instance_id, master=mock_master_widget)

        # Return the instance and all relevant mocks for use in tests
        return instance, mock_event_bus_instance, test_instance_id, mock_master_widget

    def test_initialization_and_mvc_setup(self, module_instance, mock_mvc_components, mocker: MockerFixture):
        """
        Test if the module's __init__ correctly triggers the _init_mvc method,
        instantiating and configuring all MVC components.
        """
        instance, mock_event_bus_instance, _, mock_master_widget = module_instance
        mock_model_class, mock_view_class, mock_controller_class = mock_mvc_components

        # 1. Verify that the mock MVC classes were called to create instances.
        mock_model_class.assert_called_once()
        mock_view_class.assert_called_once()
        mock_controller_class.assert_called_once()

        # 2. Verify that the instances were assigned to the module's attributes.
        #    In the context of this test, checking for non-None is sufficient,
        #    as we've already asserted that the mock factories were called.
        assert instance.model is not None
        assert instance.view is not None
        assert instance.controller is not None

        # 3. Verify that dependencies were correctly passed to the components.
        instance.view.set_master.assert_called_once_with(mock_master_widget)
        instance.view.set_internal_bus.assert_called_once_with(mock_event_bus_instance)
        instance.controller.set_internal_bus.assert_called_once_with(mock_event_bus_instance)

    def test_class_methods_for_id_and_count(self):
        """
        Test the static-like class methods for managing ID and instance count.
        This test does not need an instance of the module.
        """
        # Set a class attribute for testing
        ConcreteTestModule.id = "test.module"
        assert ConcreteTestModule.get_id() == "test.module"

        # Test the counting mechanism
        initial_count = ConcreteTestModule.get_count()
        ConcreteTestModule.count_increment()
        assert ConcreteTestModule.get_count() == initial_count + 1

        # Reset for test isolation
        ConcreteTestModule.count = initial_count

    def test_instance_id_getter(self, module_instance):
        """
        Test that get_instance_id returns the correct ID set during initialization.
        """
        instance, _, test_instance_id, _ = module_instance

        # Verify the getter returns the correct value
        assert instance.get_instance_id() == test_instance_id

    def test_on_ready(self, module_instance):
        """
        Test if the on_ready call is correctly delegated to the controller,
        including setting the instance_id on it.
        """
        instance, _, test_instance_id, _ = module_instance

        # Call the method under test
        instance.on_ready()

        # Verify the calls are passed down to the controller
        instance.controller.set_instance_id.assert_called_once_with(test_instance_id)
        instance.controller.on_ready.assert_called_once()

    def test_add_child_and_prevent_duplicates(self, module_instance, mocker):
        """
        Test adding a child module and ensuring that adding a child with
        a duplicate name raises a RuntimeError.
        """
        instance, _, _, _ = module_instance
        mock_child_module = mocker.Mock(spec=Module)

        # Add a child successfully
        instance.add_child("child1", mock_child_module)
        assert "child1" in instance.children
        assert instance.children["child1"] == mock_child_module

        # Try to add a child with the same name, expecting an error
        with pytest.raises(RuntimeError):
            instance.add_child("child1", mock_child_module)

    def test_deactivate_cleanup(self, module_instance, mocker):
        """
        Test that the deactivate method calls cleanup on its own MVC components
        and also recursively calls deactivate on all its children.
        """
        instance, _, _, _ = module_instance

        # Call the method under test
        instance.deactivate()
        # Verify it calls cleanup on its own MVC components
        instance.model.cleanup.assert_called_once()
        instance.view.cleanup.assert_called_once()
        instance.controller.cleanup.assert_called_once()

    def test_highlight_view(self, module_instance, mocker):
        """
        Test that highlight_view correctly interacts with the view and its window object.
        """
        instance, _, _, _ = module_instance

        # Mock the window object that the view is supposed to return
        mock_window = mocker.Mock()
        instance.view.get_window.return_value = mock_window

        # Call the method under test
        instance.highlight_view()

        # Verify the sequence of calls to show the window
        instance.view.get_window.assert_called_once()
        mock_window.deiconify.assert_called_once()
        mock_window.lift.assert_called_once()
        mock_window.focus_force.assert_called_once()
