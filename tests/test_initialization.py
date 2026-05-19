import pytest
import logging
import semanticpy

logger = logging.getLogger(__name__)


def test_initialization_without_profile():
    with pytest.raises(TypeError) as exception:
        semanticpy.Model.factory(globals={})

        assert (
            str(exception)
            == "Model.factory() missing 1 required positional argument: 'profile'"
        )


def test_initialization_with_valid_profile():
    semanticpy.Model.factory(
        profile="linked-art",
        globals={},
    )


def test_initialization_with_valid_profile_no_globals():
    model = semanticpy.Model.factory(
        profile="linked-art",
        globals=None,
    )

    assert hasattr(model, "HumanMadeObject")


def test_initialization_with_invalid_profile():
    with pytest.raises(semanticpy.SemanticPyError) as exception:
        semanticpy.Model.factory(
            profile="does-not-exist",
            globals={},
        )

        assert str(exception).startswith("The specified profile")
        assert str(exception).endswith("does not exist!")


def test_teardown():
    """Test tearing down the model and removing the model classes from globals."""

    # First create the models through the factory method, and add classes to globals
    semanticpy.Model.factory(
        profile="linked-art",
        globals=globals(),
    )

    # Check that one of the profile's model classes has been added to globals()
    assert "HumanMadeObject" in globals()

    # After running the factory method and creating the model, create a model instance;
    # this should succeed as the model class name has been added to globals()
    obj = HumanMadeObject()

    assert isinstance(obj, HumanMadeObject)

    # Now tear the model down, restoring globals() to its prior state
    semanticpy.Model.teardown(globals=globals())

    # Check that one of the profile's model classes has been removed from globals()
    assert not "HumanMadeObject" in globals()

    # Then try to create a model instance again, which should fail if the teardown was
    # successful, and if the restoration of globals() to its prior state succeeded
    try:
        obj = HumanMadeObject()

        assert isinstance(obj, HumanMadeObject)
    except NameError as exception:
        assert str(exception) == "name 'HumanMadeObject' is not defined"
