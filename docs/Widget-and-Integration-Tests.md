# Widget and Integration Tests
Relevant source files
- [test/check_progress_indicator.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py)
- [test/dropdown.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/dropdown.py)
- [test/marktest.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py)
- [test/test_expandable_state.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py)
- [test/test_lambda.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_lambda.py)
- [test/test_virtual_grid.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py)

This section covers the integration and functional testing of high-level components within the PyThra Framework. Unlike unit tests for the reconciler, these tests verify the interaction between `State` lifecycles, widget controllers, property rendering, and the Python-to-JavaScript initialization bridge.

## Overview of Integration Testing

Widget integration tests in PyThra typically focus on three areas:

1. **State Persistence**: Ensuring that `State` objects are correctly preserved across parent rebuilds [test/test_expandable_state.py72-77](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L72-L77)
2. **Controller Logic**: Verifying that imperative controllers (e.g., `ProgressIndicatorController`) correctly update the internal widget state and subsequent render properties [test/check_progress_indicator.py14-21](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L14-L21)
3. **JS Initialization Bridge**: Validating that the `_js_init` dictionary, which contains the configuration for the browser-side engines, is correctly populated during the `render_props()` call [test/check_progress_indicator.py40-45](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L40-L45)

## State Persistence and Lifecycle Tests

The `test_expandable_state.py` file demonstrates how to verify that a `StatefulWidget` maintains its internal state when its parent triggers a reconciliation cycle.

### Implementation Detail: Mocking the Environment

To run these tests without a GUI environment, a `MockWindow` is used to intercept JavaScript execution calls [test/test_expandable_state.py5-9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L5-L9) The `Framework` is then manually driven through its reconciliation phases:

- `_perform_initial_render()`: Bootstraps the widget tree [test/test_expandable_state.py51](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L51-L51)
- `_process_reconciliation()`: Synchronously flushes the `_pending_state_updates` queue [test/test_expandable_state.py62](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L62-L62)

### State Retention Workflow

The following diagram illustrates how the test verifies that the `Expandable` widget's state instance remains identical even after the `MockHomePage` (parent) increments its own counter and rebuilds.

**State Persistence Verification**

```

```

Sources: [test/test_expandable_state.py17-78](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_expandable_state.py#L17-L78)

## Progress Indicator and Controller Tests

The `check_progress_indicator.py` script verifies the data flow from a `ProgressIndicatorController` to the rendered HTML properties.

### Key Assertions

- **Visibility Toggle**: Ensuring `controller.hide()` and `controller.show()` correctly update the `visible` boolean [test/check_progress_indicator.py17-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L17-L20)
- **Engine Configuration**: Verifying that `render_props()` includes the `_js_init` key, which specifies the `PythraProgressIndicator` engine and the specific `LoaderStyle`[test/check_progress_indicator.py40-44](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L40-L44)

PropertySourceExpected Value (Example)`class``LoaderStyle``loader-arcade-1``engine``_js_init``PythraProgressIndicator``loader``Loader``arcade`
Sources: [test/check_progress_indicator.py25-45](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/check_progress_indicator.py#L25-L45)

## Complex Widget Integration: Markdown Editor

The `marktest.py` file provides a blueprint for integrating complex plugins like the `MarkdownEditor`. It highlights a critical pattern for performance: **Static Subtree Caching**.

### Static Layout Pattern

To prevent the reconciler from diffing complex, stable UI structures (like toolbars or editor containers), the test demonstrates caching the widget tree in the `State` constructor:

1. Initialize the `MarkdownEditorController` and `MarkdownEditor` widget once in `__init__`[test/marktest.py48-58](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L48-L58)
2. Wrap the editor in a `Container` tree and store the entire tree as `self.editor_layout`[test/marktest.py64-81](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L64-L81)
3. Return the cached `self.editor_layout` in the `build()` method to ensure the reconciler identifies it as the same object, skipping deep diffing [test/marktest.py246](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L246-L246)

Sources: [test/marktest.py44-82](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L44-L82)[test/marktest.py246](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/marktest.py#L246-L246)

## Virtualized Grid Testing

The `test_virtual_grid.py` file verifies the `VirtualGridView` implementation. This test is unique as it launches a full `Framework` instance to check the virtualization logic for large datasets (1,000 items) [test/test_virtual_grid.py38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py#L38-L38)

### Data Flow for Virtualization

```

```

Sources: [test/test_virtual_grid.py25-60](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_virtual_grid.py#L25-L60)

## Interactive Dropdown Tests

The `test/dropdown.py` file contains multiple examples of `VirtualDropdown` usage, testing different themes and item configurations.

### Configuration Validation

Tests verify that `VirtualDropdownTheme` correctly propagates CSS values such as `backgroundColor`, `borderRadius`, and `dropdownMargin` to the underlying widget [test/dropdown.py76-89](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/dropdown.py#L76-L89) It also ensures that the `onChanged` callback correctly receives the selected value from the JavaScript bridge via a lambda or method reference [test/dropdown.py75](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/dropdown.py#L75-L75)

### Lambda Callback Note

A specific test case in `test_lambda.py` explores the behavior of Python lambdas when used as callbacks. It confirms that if a callback expects arguments (like `TapDetails`), a simple `lambda: print()` will raise a `TypeError`, necessitating the use of `lambda _: ...` or named functions [test/test_lambda.py1-10](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_lambda.py#L1-L10)

Sources: [test/dropdown.py68-90](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/dropdown.py#L68-L90)[test/test_lambda.py1-10](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/test/test_lambda.py#L1-L10)