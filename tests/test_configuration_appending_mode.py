from semanticpy import Model, AppendingMode


def test_appending_mode_always():
    """Test the library's multiple-value property appending mode configuration."""

    # Instantiate the model with the desired profile
    model = Model.factory(profile="linked-art")

    # Configure the append mode to "Always" (this is the default value, so does not need setting)
    # The option can be set via name or enumeration option; all of these ways are valid:
    Model.configure(appending="Always")
    Model.configure(appending="always")
    Model.configure(appending="ALWAYS")
    Model.configure(appending=AppendingMode.Always)

    # Create an instance to demonstrate the various multiple-value property appending modes
    object = model.HumanMadeObject()

    # Notice that the list of identifiers is initially unset (None)
    assert object.identified_by is None

    # Create an instance to demonstrate the various multiple-value property appending modes
    identifier = model.Identifier(content="123")

    # Assign the identifier to the `object.identified_by` property
    object.identified_by = identifier

    # Notice that the list of identifiers has grown to accommodate the new identifier
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier

    # Assign the identifier to the `object.identified_by` property again
    object.identified_by = identifier

    # Notice that the list of identifiers has grown again to accommodate the duplicate
    # due to the Model currently being configured to append values regardless of dupes:
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 2
    assert object.identified_by[1] is identifier

    # Tear down the model, removing it from the current scope and reset configuration
    Model.teardown()


def test_appending_mode_unique():
    """Test the library's multiple-value property appending mode configuration."""

    # Instantiate the model with the desired profile
    model = Model.factory(profile="linked-art")

    # Configure the append mode to "Always" (this is the default value, so does not need setting)
    # The option can be set via name or enumeration option; all of these ways are valid:
    Model.configure(appending="Unique")
    Model.configure(appending="unique")
    Model.configure(appending="UNIQUE")
    Model.configure(appending=AppendingMode.Unique)

    # Create an instance to demonstrate the various multiple-value property appending modes
    object = model.HumanMadeObject()

    # Notice that the list of identifiers is initially unset (None)
    assert object.identified_by is None

    # Create an instance to demonstrate the various multiple-value property appending modes
    identifier = model.Identifier(content="123")

    # Assign the identifier to the `object.identified_by` property
    object.identified_by = identifier

    # Notice that the list of identifiers has grown to accommodate the new identifier
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier

    # Attempt to assign the identifier to the `object.identified_by` property again
    object.identified_by = identifier

    # Notice that the list of identifiers has not grown to accommodate the duplicate
    # due to the Model currently being configured to only append unique values:
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier

    # Tear down the model, removing it from the current scope and reset configuration
    Model.teardown()
