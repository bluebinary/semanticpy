import pytest
import os
import sys

# Add the library source path to sys.path so that the library can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

import semanticpy


@pytest.fixture(scope="session", name="data")
def data() -> callable:
    """Create a fixture that can be used to obtain the contents of example data files as
    strings or bytes by specifying the path relative to the /tests/data folder."""

    def fixture(path: str, binary: bool = False) -> str:
        """Read the specified data file, returning its contents either as a string value
        or if requested in binary mode returning the encoded bytes value."""

        if not isinstance(path, str):
            raise TypeError("The 'path' argument must have a string value!")

        if not isinstance(binary, bool):
            raise TypeError("The 'binary' argument must have a boolean value!")

        filepath: str = os.path.join(os.path.dirname(__file__), "data", path)

        if not os.path.exists(filepath):
            raise ValueError(
                f"The requested example file, '{filepath}', does not exist!"
            )

        # If binary mode has been specified, adjust the read mode accordingly
        mode: str = "rb" if binary else "r"

        with open(filepath, mode) as handle:
            return handle.read()

    return fixture


@pytest.fixture(scope="session", name="path")
def path() -> callable:
    """Create a fixture that can be used to obtain the path for example data files as
    by specifying the path relative to the /tests/data folder."""

    def fixture(path: str) -> str:
        """Read the specified data file, returning its contents either as a string value
        or if requested in binary mode returning the encoded bytes value."""

        if not isinstance(path, str):
            raise TypeError("The 'path' argument must have a string value!")

        filepath: str = os.path.join(os.path.dirname(__file__), "data", path)

        if not os.path.exists(filepath):
            raise ValueError(
                f"The requested example file, '{filepath}', does not exist!"
            )

        return filepath

    return fixture


@pytest.fixture(scope="module", name="factory")
def factory() -> callable:
    # Using a fixture factory the profile and globals can be overridden if needed

    def fixture(profile: str = "linked-art", globals: dict = globals()):
        return semanticpy.Model.factory(
            profile=profile,
            globals=globals,
        )

    return fixture
