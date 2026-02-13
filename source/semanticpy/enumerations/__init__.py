from enumerific import Enumeration, auto


class OverwriteMode(Enumeration):
    """This enumeration defines the overwrite mode behaviours for properties that accept
    single values, in terms of how the library should handle value reassignment."""

    Allow = auto(
        description="Allow single-value properties to have their values be overwritten.",
        default=True,
    )

    Warning = auto(
        description="Emit a warning when single-value properties are overwritten."
    )

    Prevent = auto(
        description="Prevent single-value properties from being overwritten and emit a warning."
    )

    PreventQuietly = auto(
        description="Prevent single-value properties from being overwritten with no logging."
    )

    Error = auto(
        description="Raise an exception when single-value properties are overwritten."
    )


class AppendingMode(Enumeration):
    """This enumeration defines the appending mode behaviours for properties that accept
    multiple values, in terms of how the library should handle value assignment."""

    Always = auto(
        description="Always append values to multiple-value properties regardless of if the value has been previously appended or not.",
        default=True,
    )

    Unique = auto(
        description="Only append values to multiple-value properties that have not previously been appended to the same property."
    )
