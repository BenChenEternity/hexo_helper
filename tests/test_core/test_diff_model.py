import pytest

from src.hexo_helper.core.mvc.model import DiffModel


# A pytest fixture to provide a fresh, initialized model for each test method.
# It's defined outside the class but can be used by methods within it.
@pytest.fixture
def user_model() -> DiffModel:
    model = DiffModel()
    model.init({"username": "jdoe", "email": "jdoe@example.com", "age": 30, "active": True})
    return model


class TestDiffModel:
    """
    Test suite for the DiffModel class.
    """

    # Test Group 1: Initialization and Basic State
    # =================================================

    def test_initialization(self):
        """Tests the model's initial state upon creation."""
        model = DiffModel()
        assert not hasattr(model, "username")
        assert model._origin == {}
        assert model._dirty_fields == set()
        assert not model.is_dirty()

    def test_set_origin(self, user_model):
        """Tests that set_origin correctly populates attributes and the origin state."""
        assert user_model.username == "jdoe"
        assert user_model.age == 30
        assert user_model._origin["username"] == "jdoe"
        assert not user_model.is_dirty()
        assert user_model.to_dict() == {"username": "jdoe", "email": "jdoe@example.com", "age": 30, "active": True}

    # Test Group 2: Getters and Setters
    # ===============================================

    def test_get_value(self, user_model):
        """Tests retrieving existing values."""
        assert user_model.get("username") == "jdoe"
        assert user_model.get("age") == 30

    def test_get_non_existent_attribute_raises_error(self, user_model):
        """Tests that getting a non-existent key raises an AttributeError."""
        with pytest.raises(AttributeError, match="'non_existent_key' doesn't exist"):
            user_model.get("non_existent_key")

    def test_set_non_existent_attribute_raises_error(self, user_model):
        """Tests that setting a non-existent key raises an AttributeError."""
        with pytest.raises(AttributeError, match="'new_field' doesn't exist"):
            user_model.set("new_field", "some_value")

    def test_set_value_and_dirty_tracking(self, user_model):
        """Tests setting a value and verifies dirty state tracking."""
        user_model.set("age", 31)
        assert user_model.get("age") == 31
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"age"}

    def test_set_value_to_same_value_does_not_mark_dirty(self, user_model):
        """Tests that setting a field to its current value doesn't change dirty state."""
        assert not user_model.is_dirty()
        user_model.set("username", "jdoe")
        assert not user_model.is_dirty()
        assert user_model.get_dirty_fields() == set()

    def test_set_value_back_to_original_removes_dirty_flag(self, user_model):
        """Tests that reverting a field to its original value cleans its dirty state."""
        user_model.set("age", 31)
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"age"}

        user_model.set("age", 30)
        assert not user_model.is_dirty()
        assert user_model.get_dirty_fields() == set()

    # Test Group 3: Bulk and State Operations
    # ===================================================

    def test_update_multiple_fields(self, user_model):
        """Tests the update method for modifying multiple fields."""
        user_model.update({"username": "john.doe", "age": 32})
        assert user_model.get("username") == "john.doe"
        assert user_model.get("age") == 32
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"username", "age"}

    def test_to_dict_method(self, user_model):
        """Tests that to_dict returns the current state and excludes internal attributes."""
        user_model.set("email", "new.email@example.com")
        expected_dict = {"username": "jdoe", "email": "new.email@example.com", "age": 30, "active": True}
        assert user_model.to_dict() == expected_dict
        assert "_origin" not in user_model.to_dict()
        assert "dirty_fields" not in user_model.to_dict()

    def test_cleanup_reverts_changes(self, user_model):
        """Tests that cleanup reverts all changes and clears dirty state."""
        user_model.update({"username": "john.doe", "active": False})
        assert user_model.is_dirty()

        user_model.cleanup()

        assert not user_model.is_dirty()
        assert user_model.get("username") == "jdoe"
        assert user_model.get("active") is True
        assert user_model.get_dirty_fields() == set()

    def test_cleanup_with_no_changes(self, user_model):
        """Tests that cleanup does nothing when the model is not dirty."""
        initial_dict = user_model.to_dict()
        user_model.cleanup()
        assert not user_model.is_dirty()
        assert user_model.to_dict() == initial_dict

    def test_apply_persists_changes(self, user_model):
        """Tests that apply makes current changes the new original state."""
        user_model.set("age", 35)
        assert user_model.get_dirty_fields() == {"age"}

        user_model.apply()

        assert not user_model.is_dirty()
        assert user_model.get_dirty_fields() == set()
        assert user_model._origin["age"] == 35
        assert user_model.get("age") == 35

        user_model.set("age", 30)
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"age"}

    def test_apply_with_no_changes(self, user_model):
        """Tests that apply does nothing if the model is not dirty."""
        initial_origin = user_model._origin.copy()
        user_model.apply()
        assert not user_model.is_dirty()
        assert user_model._origin == initial_origin

    # Test Group 4: Complex Workflow
    # ============================================

    def test_complex_workflow(self, user_model):
        """Simulates a more complex sequence of operations."""
        assert not user_model.is_dirty()

        user_model.update({"username": "johndoe", "age": 31})
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"username", "age"}

        user_model.apply()
        assert not user_model.is_dirty()
        assert user_model.get("username") == "johndoe"
        assert user_model._origin["username"] == "johndoe"

        user_model.set("email", "jd@work.com")
        user_model.set("age", 32)
        assert user_model.is_dirty()
        assert user_model.get_dirty_fields() == {"email", "age"}

        user_model.cleanup()
        assert not user_model.is_dirty()
        assert user_model.get("email") == "jdoe@example.com"
        assert user_model.get("age") == 31
        assert user_model.get("username") == "johndoe"
