import pytest
import os
import sys

# Add the library source path to sys.path so that the library can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

import semanticpy


@pytest.fixture(scope="module")
def factory() -> callable:
    # Using a fixture factory the profile and globals can be overridden if needed

    def _factory(profile: str = "linked-art", globals: dict = globals()):
        return semanticpy.Model.factory(
            profile=profile,
            globals=globals,
        )

    return _factory
