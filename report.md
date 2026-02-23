# Investigation Report: Expandable Widget State Loss

## Issue Summary
When the `Expandable` widget manages its own internal state via `ExpandableState.toggle()`, interacting with other widgets in the parent `HomePage` (like sliding the slider or typing in the text field) causes the `Expandable` widget to suddenly lose its expanded state, reverting to its `initiallyExpanded` value and breaking local state preservation. 

## Root Cause Analysis
This is a framework-level issue in the Pythra Toolkit related to how `StatefulWidget` instances are processed during a parent's rebuild. The sequence of events leading to the bug is as follows:

1. **Rebuilding the Widget Tree:** When a user interacts with a widget that triggers `setState()` on `HomePageState`, Pythra calls `Framework._build_widget_tree(widget_to_rebuild)`. 
2. **Fresh Instantiation:** The `HomePageState.build()` method returns a new widget tree containing a freshly instantiated `Expandable(initiallyExpanded=self.is_expanded)`.
3. **New State Creation:** Because `StatefulWidget`'s constructor (`__init__`) immediately calls `self.createState()`, the new `Expandable` widget creates a **brand-new** `ExpandableState` instance.
4. **Local State Erasure in Pre-Pass:** The `_build_widget_tree` method encounters the new `Expandable` widget and calls its `build()` method using the **new** state, which initializes `self.is_expanded` using the `initiallyExpanded` prop (ignoring any previous toggles). The subtree is fully built offline before reconciliation even starts.
5. **Reconciliation Misses State Preservation:** During the `reconciler.reconcile()` phase, the framework matches the old `Expandable` widget with the new one. It calls the lifecycle hook `didUpdateWidget(old_widget, new_widget)` on the *new* state, but it **fails to transfer the old `State` instance to the new widget**. 

Because the old `State` instance (which held the true runtime `is_expanded` value) is never copied over to the new widget tree, it gets replaced by the fresh state and garbage-collected. This is analogous to a React component losing state when its key changes, but here it happens on every parent rebuild because of how `StatefulWidget`s are orchestrated.

## Why Does `HomePageState` Survive?
`HomePage` is rendered efficiently at the root level (or wrapped closely). It is not repeatedly re-instantiated by a parent's `build()` method when its own `setState()` is fired. The Framework loops through `_pending_state_updates` without creating a new `HomePage`, hence preserving its `HomePageState`. 

## Callback Reference Changes
On top of state loss, `Expandable` leverages `GestureDetector` for its `onTap` events. `GestureDetector` automatically names its callbacks based on its unique instance id (`f"gd_tap_{id(self)}"`). Since a new `GestureDetector` is instantiated on every parent rebuild, the callback name updates dynamically. The framework successfully patches this in the DOM (registering the new callback pointing to the *new* state instance's `toggle()`), explaining why the widget *can* be toggled again, but only operates on the wiped local state.

## Recommendations

### 1. The Real Fix: Framework Refactor
To mirror Flutter's state preservation properly, Pythra's core rendering (`core.py` and `reconciler.py`) needs architectural modifications:
* **Decouple State Creation from Instantiation:** `StatefulWidget` should not create its `State` immediately in `__init__`. 
* **State Transference in Reconciler:** The `_build_widget_tree` and `reconciler` must work together. When diffing the tree, if the reconciler identifies a matching `StatefulWidget` (same `Key` and type), it should retrieve the *old* `State`, update its `widget` property to the newly constructed widget configuration, call `didUpdateWidget()`, and **then** call `old_state.build()`.

### 2. Immediate Workaround for the App
Until the framework correctly transfers `State` objects between widget rebuilds, the standard workaround is to **lift state up**—meaning no local state mutations should be kept inside sub-widgets if a parent rebuild is expected.

In your `main.py`, you are already partially doing this by using `HomePageState` to track `self.is_expanded` and passing `initiallyExpanded=self.is_expanded`. To fully implement this workaround and avoid desyncs:
* Ensure `Expandable` is purely driven by `HomePageState`.
* Pass `onToggle=self.toggle` explicitly, as you've done. This guarantees that `ExpandableState.toggle` is never used, forcing all toggles to route through `HomePageState`, which acts as a reliable single source of truth.
