from enumerific import Enumeration, auto


class OverwriteMode(Enumeration):
    """This enumeration defines the overwrite mode behaviours for properties that accept
    single values, in terms of how the library should handle value reassignment."""

    Allow = auto(
        description="Allow single-value properties to have their values be overwritten",
        default=True,
    )

    Warning = auto(
        description="Emit a warning when single-value properties are overwritten"
    )

    Prevent = auto(
        description="Prevent single-value properties from being overwritten and emit a warning"
    )

    Error = auto(
        description="Raise an exception when single-value properties are overwritten"
    )
