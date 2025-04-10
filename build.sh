#!/bin/sh

# See https://share.getty.edu/display/SOFTARCH/Using+the+Nexus+Package+Manager+with+Getty+Packages for how to configure twine to publish

# Run the unit tests, refusing to deploy if the unit tests fail
if ! docker compose run tests; then
	echo -e "The unit tests failed; cannot publish!";
	exit 1;
fi

# Install the build requirements (twine, wheel)
pip install --requirement requirements.distribution.txt

rm -Rrf dist/*

## Build the library
if ! python -m build; then
    echo -e "The build failed; cannot publish!";
    exit 1;
fi

## Test the build is valid
if ! twine check dist/*; then
    echo -e "The build check tests failed; cannot publish!";
    exit 1;
fi

## upload to getty nexus registry
twine upload --repository-url "https://artifacts.getty.edu/repository/jpgt-pypi/" dist/*

## install semanticpy locally from getty nexus registry
# pip install -i https://artifacts.getty.edu/repository/jpgt-pypi-virtual/simple semanticpy

# pip install ./dist/semanticpy-1.0.0.tar.gz
