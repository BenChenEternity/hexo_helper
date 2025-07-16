# flake8: noqa
import pytest

from src.hexo_helper.exceptions import ServiceNotFoundException
from src.hexo_helper.service.constants import EVENT_REQUEST_SERVICE
from src.hexo_helper.services_manager import ServiceManager


class TestServiceManager:
    @pytest.fixture
    def mock_consumer(self, mocker):
        """fixture to mock ServiceConsumer"""
        mock_consumer_instance = mocker.Mock()
        mocker.patch("src.hexo_helper.services_manager.ServiceConsumer", return_value=mock_consumer_instance)
        return mock_consumer_instance

    def test_initialization(self, mock_consumer):
        """init"""
        manager = ServiceManager()

        assert manager.services == {}
        assert manager.consumer == mock_consumer

        # subscribe service request event
        mock_consumer.subscribe.assert_called_once_with(EVENT_REQUEST_SERVICE, manager._on_service_requested)

    def test_register_service(self, mock_consumer, mocker):
        """register"""
        manager = ServiceManager()
        mock_service = mocker.Mock()
        mock_service.name = "test_service"
        # register
        manager.register(mock_service)

        assert len(manager.services) == 1
        # find service
        assert manager.services["test_service"] == mock_service

    def test_on_service_requested_success(self, mock_consumer, mocker):
        manager = ServiceManager()
        mock_service = mocker.Mock()
        mock_service.name = "executor_service"
        mock_service.exec.return_value = "execution_result"
        manager.register(mock_service)

        # prepare payload
        action_payload = {"operation": "do_something", "args": {"id": 1}}

        # execute
        result = manager._on_service_requested(name="executor_service", action=action_payload)

        # service.exec was called
        mock_service.exec.assert_called_once()
        expected_call = mocker.call(action_payload)

        # compare func exec call args
        assert mock_service.exec.call_args == expected_call
        # compare value
        assert result == {"executor_service": "execution_result"}

    def test_on_service_requested_not_found_raises_exception(self, mock_consumer):
        manager = ServiceManager()
        with pytest.raises(ServiceNotFoundException):
            manager._on_service_requested(name="non_existent_service", action={"operation": "do_nothing"})

    def test_on_service_requested_with_no_action(self, mock_consumer, mocker):
        """if action is empty"""
        manager = ServiceManager()
        mock_service = mocker.Mock()
        mock_service.name = "idle_service"
        manager.register(mock_service)

        result_none = manager._on_service_requested(name="idle_service", action=None)
        assert result_none is None

        result_empty = manager._on_service_requested(name="idle_service", action={})
        assert result_empty is None

        mock_service.exec.assert_not_called()

    def test_startup_all_services(self, mock_consumer, mocker):
        """start services"""
        manager = ServiceManager()
        mock_service_1 = mocker.Mock(name="service1")
        mock_service_2 = mocker.Mock(name="service2")
        manager.register(mock_service_1)
        manager.register(mock_service_2)

        manager.start_up()

        mock_service_1.start.assert_called_once()
        mock_service_2.start.assert_called_once()

    def test_shutdown_all_services(self, mock_consumer, mocker):
        """test shutdown"""
        manager = ServiceManager()
        mock_service_1 = mocker.Mock(name="service1")
        mock_service_2 = mocker.Mock(name="service2")
        manager.register(mock_service_1)
        manager.register(mock_service_2)

        manager.shutdown()

        mock_service_1.shutdown.assert_called_once()
        mock_service_2.shutdown.assert_called_once()
