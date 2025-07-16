import pytest

from src.hexo_helper.common.module import Module


class ConcreteTestModule(Module):
    """A concrete Module subclass for instantiation during tests."""

    # This method will be mocked during tests to control what MVC components are returned
    @classmethod
    def get_mvc(cls):
        # This base implementation should not be called in tests
        raise NotImplementedError


class TestModule:
    """
    Unit test suite for the abstract Module class.
    """

    @pytest.fixture
    def mock_mvc_components(self, mocker):
        """
        A fixture that creates mock classes for Model, View, and Controller.
        """
        # Create mock classes. When these are instantiated, they will return a mock instance.
        mock_model_class = mocker.Mock()
        mock_view_class = mocker.Mock()
        mock_controller_class = mocker.Mock()
        return mock_model_class, mock_view_class, mock_controller_class

    @pytest.fixture
    def module_instance(self, mocker, mock_mvc_components):
        """
        A fixture that provides a fully initialized instance of ConcreteTestModule
        with all its dependencies (MVC, EventBus) mocked out.
        """
        mock_model_class, mock_view_class, mock_controller_class = mock_mvc_components

        # Patch the get_mvc method of our concrete class to return the mock classes
        mocker.patch.object(
            ConcreteTestModule, "get_mvc", return_value=(mock_model_class, mock_view_class, mock_controller_class)
        )

        # Patch EventBus so we can verify it's created and used
        mock_event_bus_instance = mocker.Mock()
        mocker.patch("src.hexo_helper.common.module.EventBus", return_value=mock_event_bus_instance)

        # Instantiate the module. This will trigger __init__ and _init_mvc
        instance = ConcreteTestModule()
        return instance, mock_event_bus_instance

    def test_initialization_and_mvc_setup(self, module_instance, mock_mvc_components):
        """
        Test if the module correctly initializes its MVC components via _init_mvc.
        """
        instance, mock_event_bus_instance = module_instance
        mock_model_class, mock_view_class, mock_controller_class = mock_mvc_components

        # 1. Verify that the MVC classes were instantiated
        mock_model_class.assert_called_once()
        mock_view_class.assert_called_once()
        mock_controller_class.assert_called_once()

        # 2. Verify that the instances are assigned to the correct attributes
        assert instance.model is not None
        assert instance.view is not None
        assert instance.controller is not None

        # 3. Verify that the internal event bus was passed to the view and controller
        instance.view.set_internal_bus.assert_called_once_with(mock_event_bus_instance)
        instance.controller.set_internal_bus.assert_called_once_with(mock_event_bus_instance)

    def test_class_methods_for_id_and_count(self):
        """
        Test the static-like class methods for ID and counting.
        """
        # Set a class attribute for testing
        ConcreteTestModule.id = "test.module"
        assert ConcreteTestModule.get_id() == "test.module"

        # Test counting mechanism
        initial_count = ConcreteTestModule.get_count()
        ConcreteTestModule.count_increment()
        assert ConcreteTestModule.get_count() == initial_count + 1

        # Reset for test isolation
        ConcreteTestModule.count = initial_count

    def test_instance_id_management(self, module_instance):
        """
        Test the setter and getter for the instance_id.
        """
        instance, _ = module_instance
        test_id = "main.settings@1"

        # Call the setter
        instance.set_instance_id(test_id)

        # Verify the instance_id attribute is set
        assert instance.instance_id == test_id

        # Verify the call is passed down to the controller
        instance.controller.set_instance_id.assert_called_once_with(test_id)

        # Verify the getter returns the correct value
        assert instance.get_instance_id() == test_id

    def test_set_master(self, module_instance, mocker):
        """
        Test if the set_master call is correctly passed to the view.
        """
        instance, _ = module_instance
        mock_master_widget = mocker.Mock()

        instance.set_master(mock_master_widget)

        instance.view.set_master.assert_called_once_with(mock_master_widget)

    def test_on_ready(self, module_instance):
        """
        Test if the on_ready call is correctly passed to the controller.
        """
        instance, _ = module_instance

        instance.on_ready()

        instance.controller.on_ready.assert_called_once()

    def test_add_child_and_prevent_duplicates(self, module_instance, mocker):
        """
        Test adding a child module and handling of duplicate names.
        """
        instance, _ = module_instance
        mock_child_module = mocker.Mock(spec=Module)

        # Add a child successfully
        instance.add_child("child1", mock_child_module)
        assert instance.children["child1"] == mock_child_module

        # Try to add a child with the same name, expecting an error
        with pytest.raises(RuntimeError, match="Module (child1) already exists"):
            instance.add_child("child1", mock_child_module)

    def test_deactivate_recursive_cleanup(self, module_instance, mocker):
        """
        Test that deactivate calls cleanup on its components and recursively on its children.
        """
        instance, _ = module_instance

        # Create a mock child and add it
        mock_child_module = mocker.Mock(spec=Module)
        instance.add_child("child1", mock_child_module)

        # Call deactivate
        instance.deactivate()

        # 1. Verify it calls deactivate on its children
        mock_child_module.deactivate.assert_called_once()

        # 2. Verify it calls cleanup on its own MVC components
        instance.model.cleanup.assert_called_once()
        instance.view.cleanup.assert_called_once()
        instance.controller.cleanup.assert_called_once()

    def test_highlight_view(self, module_instance, mocker):
        """
        Test that highlight_view correctly interacts with the view and its window.
        """
        instance, _ = module_instance

        # Mock the window object that the view is supposed to return
        mock_window = mocker.Mock()
        instance.view.get_window.return_value = mock_window

        instance.highlight_view()

        # Verify the sequence of calls
        instance.view.get_window.assert_called_once()
        mock_window.deiconify.assert_called_once()
        mock_window.lift.assert_called_once()
        mock_window.focus_force.assert_called_once()
