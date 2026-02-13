# Changelog
All notable changes to this project will be documented in this file.

## [1.2.6] - 2026-02-12
### Added
- Support for controlling appending behaviour for multiple-value properties.
- Support for quietly preventing overwrites of single-value properties, with no logging.

## [1.2.5] - 2026-02-12
### Added
- Improved support for aliasing properties.

## [1.2.4] - 2026-02-11
### Added
- Support for controlling overwrite behaviour for single-value properties.
- Support for Python 3.14.

## [1.2.3] - 2026-02-03
### Added
- Support for namespaced identifiers, where one or more prefixes can be registered
with the library and be used in constructing a document, with the library replacing the
prefixes with their associated URIs during document serialization.

### Updated
- Updated the Linked.Art profile document to support migration to the Linked.Art 1.0
specification and model standard.

## [1.2.2] - 2025-10-07
### Added
- Improved support for aliases, canonical property names and namespaced property names.

## [1.2.1] - 2025-04-29
### Updated
- Fixed a packaging issue that resulted in `semanticpy` library’s `/tests` subfolder
being unintentionally installed into the `site-packages` folder during installation.

## [1.2.0] - 2025-04-15
### Added
- Library and packaging improvements.
- Removed references to support for Python 3.9 or below due to incompatibilities in
these earlier versions with the union type hint operator which is used throughout the
library.
- Fixed a library import issue for running unit tests within GitHub Actions.

## [1.1.9] - 2025-04-14
### Added
- Packaged the library using `pyproject.toml` and GitHub Actions workflows to support
automatic test and distribution.

## [1.1.8] - 2025-04-11
### Added
- Improved formatting of code samples in the `README` file and noted compatibility with
Python versions 3.12 and 3.13.
- Improved packaging process to include additional package data files.

## [1.1.7] - 2025-04-10
### Added
- Improved the library including adding additional type hints, improved code documentation,
reorganized the custom type classes into their own subfolder, added the ability to load
documents from JSON-LD stored locally or via accessible URL, and updated the test suite.
- Fixed `pip install` in the build script.
- Added installation of the development and distribution dependencies into the `Dockerfile`;
added exclusion paths to the `pyproject.toml; and renamed the `requirements.deployment.txt`
dependency file to `requirements.distribution.txt`.
- Made various improvements to the library to improve readability of code, code comments,
and of error and exception messages.
- Reorganized some of the class initialization steps for improved flow.
- Improved handling of ranges.

## [1.1.6] - 2025-04-09
### Added
- Improved the build and packaging setup by migrating to the sole use of `pyproject.toml`
rather than a combination of `pyproject.toml`, `setup.cfg`, `setup.py` and `MANIFEST.in`,
simplifying and consolidating the build and setup process.

### Updated
- Rearranged the `requirements.*.txt` files, separating the dependencies into those
needed by the library (`requests`), those needed for development (`purest` and `black`)
and those needed for building and distribution (`build`, `twine` and `wheel`).

## [1.1.5] - 2024-04-06
### Added
- Added a new `teardown()` method to the `SemanticPy` class to de-initialize the model
and to remove the model class references from global state.
- Updated the `README` file to include documentation on the use of the model.
- Added unit testing to the project through PyTest which can be run through Docker for
a consistent build and test environment.
- Improved attribute error reporting to list properties available for the current model,
and removed duplicate entries from the `_special` properties list.

## [1.1.4] - 2024-01-03
### Added
- Added additional input validation in the `Model.factory()` class method for the
`profile`, `context` and `global` function arguments.

## [1.1.3] - 2023-05-22
### Added
- Improved document filtering and collation.
- Improved recursion handling.

## [1.1.0] - 2023-04-21
### Added
- Added support for cloning an existing entity via the new `clone()` instance method, and
the ability to determine if an entity is a clone via the new `is_clone` boolean property
- Added support for creating a reference to an existing entity via the new `reference()`
instance method, and the ability to determine if an entity is a reference via the new
`is_reference` boolean property
- Added support for annotating an existing entity via the new `annotate()` instance method
- Added support for obtaining an annotation via the new `annotation()` instance method
or all annotations on a model via the new `annotations()` instance method
- Added support for printing an entity's attributes and values to the console for debugging
via the new `print()` instance method
- Added support for obtaining the set of 'documents' represented by the model with the
option to filter the set based on whether they are references to other documents or a
custom callback filter method
- Added support for performing a 'walk-through' of each node in the model via the new
`walkthrough()` instance method, which can be used to recursively walk-through a model
and make changes to properties if needed

### Updated
- Updated Linked.Art profile where model entity type names are now sorted alphabetically
for easier reference

## [1.0.1] - 2023-02-15
### Added
- Updated the Linked.art profile to allow `xsd:string` in the list of range classes for
an `AttributeAssignment` entity’s `assigned_property` value as per the Linked.art model,
in addition to the default range of `crm:E55_Type`.
- Support for multiple range classes for property data type validation.

## [1.0.0] - 2022-11-22
### Added
- First release of the SemanticPy library
