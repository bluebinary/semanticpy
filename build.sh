#!/bin/sh
# See https://share.getty.edu/display/SOFTARCH/Using+the+Nexus+Package+Manager+with+Getty+Packages for how to configure twine to publish
# Install the build requirements too! (twine, wheel)
pip install -r build_requirements.txt

rm -Rrf dist/*

## build the final version
python setup.py sdist bdist_wheel

## upload to getty nexus registry
twine upload --repository-url "https://artifacts.getty.edu/repository/jpgt-pypi/" dist/*

## install semanticpy locally from getty nexus registry
# pip install -i https://artifacts.getty.edu/repository/jpgt-pypi-virtual/simple semanticpy

# pip install ./dist/semanticpy-1.0.0.tar.gz
