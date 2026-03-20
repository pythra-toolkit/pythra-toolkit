# Testing
Relevant source files
- [test/check_progress_indicator.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py)
- [test/dropdown.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/dropdown.py)
- [test/marktest.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py)
- [test/test_expandable_state.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py)
- [test/test_lambda.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_lambda.py)
- [test/test_virtual_grid.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py)

The PyThra test suite is designed to validate the integrity of the declarative rendering pipeline, the accuracy of the reconciliation engine, and the functional correctness of individual widgets. Testing is split between low-level unit tests for the diffing logic and high-level integration tests that simulate widget lifecycles and state changes.

The codebase maintains test files in two primary locations:

1. `test/`: Contains integration tests, widget verification scripts, and regression reports.
2. `src/pythra/pythra/tests/`: Contains unit tests for the core reconciler and diffing engine.

## Test Suite Architecture

The testing architecture mirrors the framework's separation of concerns, moving from the mathematical correctness of tree diffs to the visual and behavioral correctness of the UI components.

### Testing Space Mapping

The following diagram maps the testing categories to the specific code entities they validate.

**Test Category to Code Entity Mapping**

```

```

Sources: [test/test_reconciliation.py1-50](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_reconciliation.py#L1-L50)[test/test_expandable_state.py5-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L5-L15)[test/test_virtual_grid.py8-15](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py#L8-L15)

## Core Test Categories

### Reconciler and Diffing Tests

These tests focus on the `Reconciler` class and the `fast_diff` Cython module. They ensure that when a widget tree changes, the framework generates the minimum set of `Patch` operations (INSERT, REMOVE, UPDATE, MOVE, REPLACE) required to update the DOM.

- **Tree Diffing**: Validates that deep nested structures are correctly compared.
- **Key Persistence**: Ensures that widgets with the same `Key` maintain their identity and state across rebuilds.
- **Performance**: Benchmarks the Cython-accelerated diffing logic against pure Python implementations.

For details, see [Reconciler and Diffing Tests](/pythra-toolkit/pythra-toolkit/9.1-reconciler-and-diffing-tests).

### Widget and Integration Tests

These tests verify that widgets behave correctly when interacting with the `Framework` and their respective `Controller` instances. They often use `MockWindow` objects to simulate the `QWebEngineView` without requiring a full graphical environment.

- **State Persistence**: Verifies that `StatefulWidget` instances do not lose data when a parent widget rebuilds.
- **JS Initialization**: Checks that `_js_init` properties are correctly generated for interactive widgets like `ProgressIndicator`.
- **Complex Layouts**: Validates virtualization logic in `VirtualGridView` and `VirtualListView`.

For details, see [Widget and Integration Tests](/pythra-toolkit/pythra-toolkit/9.2-widget-and-integration-tests).

## Test Execution and Utilities

The test suite utilizes several patterns to facilitate testing without a live browser environment.

### Mocking the Environment

To avoid hanging on `QtWebEngine` initialization during automated tests, a `MockWindow` class is frequently used to intercept JavaScript execution calls.

[test/test_expandable_state.py5-9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L5-L9)

```

```

### Manual Verification Scripts

Several files in `test/` are designed as "Verification Scripts" that launch a full PyThra window to allow developers to manually inspect complex behaviors, such as the `MarkdownEditor` plugin or `VirtualGridView` scrolling.
FilePurposeKey Components Tested`test/check_progress_indicator.py`Validates controller visibility and JS init props.`ProgressIndicator`, `ProgressIndicatorController``test/test_virtual_grid.py`Verifies grid virtualization with 1000+ items.`VirtualGridView`, `VirtualGridController``test/marktest.py`Tests the Markdown plugin and dropdown integration.`MarkdownEditor`, `Dropdown``test/dropdown.py`Tests multiple `VirtualDropdown` instances in a single view.`VirtualDropdown`, `VirtualDropdownController`
Sources: [test/check_progress_indicator.py11-53](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L11-L53)[test/test_virtual_grid.py17-76](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py#L17-L76)[test/marktest.py44-82](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L44-L82)

## Testing Workflow

The standard workflow for testing new features involves:

1. **Unit Logic**: Adding a case to `test_reconciliation.py` if the change affects how trees are compared.
2. **Widget Integrity**: Creating a standalone script (e.g., `test_new_widget.py`) using `Framework.instance()` and `MockWindow` to verify the widget's `render_props()` and state lifecycle.
3. **Visual Verification**: Running the script with a real `app.run()` call to ensure the `pythra_bridge.js` correctly interprets the patches and initializes the JS engines.

**Framework Integration Flow**

```

```

Sources: [test/test_expandable_state.py45-79](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L45-L79)[test/check_progress_indicator.py11-46](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L11-L46)