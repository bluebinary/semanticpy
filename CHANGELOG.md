# Changelog
All notable changes to this project will be documented in this file.

## [1.1.0] - 2023-03-21
### Added
- Added support for cloning an existing entity via the new `clone()` instance method, and the ability to determine if an entity is a clone via the new `is_clone` boolean property
- Added support for creating a reference to an existing entity via the new `reference()` instance method, and the ability to determine if an entity is a reference via the new `is_reference` boolean property
- Added support for annotating an existing entity via the new `annotate()` instance method
- Added support for obtaining an annotation via the new `annotation()` instance method or all annotations on a model via the new `annotations()` instance method
- Added support for printing an entity's attributes and values to the console for debugging via the new `print()` instance method
- Added support for obtaining the set of 'documents' represented by the model with the option to filter the set based on whether they are references to other documents or a custom callback filter method
- Added support for performing a 'walk-through' of each node in the model via the new `walkthrough()` instance method, which can be used to recursively walk-through a model and make changes to properties if needed

### Updated
- Updated Linked.Art profile where model entity type names are now sorted alphabetically for easier reference

## [1.0.0] - 2023-02-02
### Added
- First release of the SemanticPy library