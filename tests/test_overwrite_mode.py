from semanticpy import Model, OverwriteMode, SemanticPyError

import logging
import pytest


def test_overwrite_mode_allow():
    """Test the library's singular property value overwrite allowed mode."""

    # Set up the model using the Linked.Art profile
    Model.factory(profile="linked-art", globals=globals())

    # By default the library is in overwrite allowed mode, but demonstrate setting here
    Model.overwrite(mode=OverwriteMode.Allow)

    # Create a new model instance to test with
    identifier = Identifier()

    assert isinstance(identifier, Identifier)

    # Assign its initial value
    identifier.content = "123"

    # Ensure that the initial value was set
    assert identifier.content == "123"

    # Overwrite its initial value; in warning mode this should generate a warning
    identifier.content = "456"

    # Ensure that the overwritten value was set
    assert identifier.content == "456"

    # Tear down the model, removing it from the current scope and reset overwrite mode
    Model.teardown(globals=globals())


def test_overwrite_mode_warning(caplog):
    """Test the library's singular property value overwrite warning mode."""

    caplog.set_level(logging.WARNING, logger="semanticpy")

    # Set up the model using the Linked.Art profile
    Model.factory(profile="linked-art", globals=globals())

    # Set the singular property value overwrite mode
    Model.overwrite(mode=OverwriteMode.Warning)

    # Create a new model instance to test with
    identifier = Identifier()

    assert isinstance(identifier, Identifier)

    # Assign its initial value
    identifier.content = "123"

    # Ensure that the initial value was set
    assert identifier.content == "123"

    # Overwrite its initial value; in warning mode this should generate a warning
    identifier.content = "456"

    # Ensure that the expected warning message was captured
    assert (
        "The 'Identifier' entity's 'content' property has already been assigned to '123', and will be overwritten with the newly provided value: '456'!"
        in caplog.text.strip()
    )

    # Ensure that the overwritten value was set
    assert identifier.content == "456"

    # Tear down the model, removing it from the current scope and reset overwrite mode
    Model.teardown(globals=globals())


def test_overwrite_mode_prevent(caplog):
    """Test the library's singular property value overwrite prevention mode."""

    caplog.set_level(logging.WARNING, logger="semanticpy")

    # Set up the model using the Linked.Art profile
    Model.factory(profile="linked-art", globals=globals())

    # Set the singular property value overwrite mode
    Model.overwrite(mode=OverwriteMode.Prevent)

    # Create a new model instance to test with
    identifier = Identifier()

    assert isinstance(identifier, Identifier)

    # Assign its initial value
    identifier.content = "123"

    # Ensure that the initial value was set
    assert identifier.content == "123"

    # Attempt to overwrite the initial value
    identifier.content = "456"

    # Ensure that the expected warning message was captured
    assert (
        "The 'Identifier' entity's 'content' property has already been assigned to '123', and current library configuration, prevents it from being overwritten!"
        in caplog.text.strip()
    )

    # As we captured the exception above, and as prevent mode
    assert identifier.content == "123"

    # Tear down the model, removing it from the current scope and reset overwrite mode
    Model.teardown(globals=globals())


def test_overwrite_mode_error():
    """Test the library's singular property value overwrite prevention mode."""

    # Set up the model using the Linked.Art profile
    Model.factory(profile="linked-art", globals=globals())

    # Set the singular property value overwrite mode
    Model.overwrite(mode=OverwriteMode.Error)

    # Create a new model instance to test with
    identifier = Identifier()

    assert isinstance(identifier, Identifier)

    # Assign its initial value
    identifier.content = "123"

    # Ensure that the initial value was set
    assert identifier.content == "123"

    # Setup PyTest to capture the expected SemanticPyError exception
    with pytest.raises(SemanticPyError) as exception:
        # Attempt to overwrite the initial value; per configuration this should error
        identifier.content = "456"

        # Ensure that the expected exception message was captured
        assert (
            str(exception)
            == "The 'Identifier' entity's 'content' property has already been assigned to '123', and current library configuration, prevents it from being overwritten!"
        )

    # As we captured the exception above, and as the property was not overwritten, the
    # property value should be the same as it was before the overwrite attempt was made
    assert identifier.content == "123"

    # Tear down the model, removing it from the current scope and reset overwrite mode
    Model.teardown(globals=globals())
