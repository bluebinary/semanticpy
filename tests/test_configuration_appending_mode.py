from semanticpy import Model, AppendingMode, Nodes


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
    assert isinstance(object.identified_by, list)
    assert isinstance(object.identified_by, Nodes)
    assert len(object.identified_by) == 0
    assert object.identified_by == []

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

    # Notice that the list of identifiers is initially empty
    assert isinstance(object.classified_as, list)
    assert isinstance(object.classified_as, Nodes)
    assert len(object.classified_as) == 0
    assert object.classified_as == []

    # Create and assign a Type
    object.classified_as = type1 = model.Type(
        ident="aat:300133025",
        label="Works of Art",
    )

    assert len(object.classified_as) == 1

    # Attempt to create and assign a Type with the same value, as
    # appending mode is set to unique, this should be ignored
    object.classified_as = type2 = model.Type(
        ident="aat:300133025",
        label="Works of Art",
    )

    # Check that the duplicate assignment was ignored
    assert len(object.classified_as) == 1
    assert object.classified_as[0] is type1
    assert object.classified_as[0] is not type2

    # Notice that the list of identifiers is initially empty
    assert isinstance(object.identified_by, list)
    assert isinstance(object.identified_by, Nodes)
    assert len(object.identified_by) == 0
    assert object.identified_by == []

    # Create an instance to demonstrate the various multiple-value property appending modes
    identifier1 = model.Identifier(content="123")

    # Assign the identifier to the `object.identified_by` property
    object.identified_by = identifier1

    # Notice that the list of identifiers has grown to accommodate the new identifier
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier1

    # Attempt to assign the identifier to the `object.identified_by` property again;
    # this is prevented by identity-comparison, as the the same instance is assigned
    object.identified_by = identifier1

    # Notice that the list of identifiers has not grown to accommodate the duplicate
    # due to the Model currently being configured to only append unique values:
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier1

    # Create another identifier instance, this time to check via equality comparison
    identifier2 = model.Identifier(content="123")

    # Attempt to assign the identifier to the `object.identified_by` property again;
    # this is prevented by equality-comparison, for new instances with the same content
    object.identified_by = identifier2

    # Notice that the list of identifiers has not grown to accommodate the duplicate
    # due to the Model currently being configured to only append unique values:
    assert isinstance(object.identified_by, list)
    assert len(object.identified_by) == 1
    assert object.identified_by[0] is identifier1
    assert object.identified_by[0] is not identifier2

    # Tear down the model, removing it from the current scope and reset configuration
    Model.teardown()
