import pytest
import semanticpy
import os


@pytest.fixture(scope="module")
def factory() -> callable:
    # Using a fixture factory the profile and globals can be overridden if needed

    def _factory(profile: str = "linked-art", globals: dict = globals()):
        return semanticpy.Model.factory(
            profile=profile,
            globals=globals,
        )

    return _factory
