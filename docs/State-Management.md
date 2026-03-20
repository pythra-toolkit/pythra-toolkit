# State Management
Relevant source files
- [src/pythra/pythra/__pycache__/api.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/api.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/server.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/server.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/state.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/state.cpython-312.pyc)
- [src/pythra/pythra/base.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py)
- [src/pythra/pythra/server.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/server.py)
- [src/pythra/pythra/state.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py)
- [todo.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/todo.md)

State management in PyThra is the "memory system" of the application, responsible for handling widgets that need to remember data and change over time, such as counters, form inputs, or navigation stacks [src/pythra/pythra/state.py8-9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L8-L9) The system follows a declarative model where UI updates are triggered by explicit state changes, which then flow through a reconciliation process to update the DOM.

### Core Entities

The state management system is built around three primary classes defined in `state.py`:
ClassRoleDescription`StatefulWidget`The "Screen"A widget that can change and "remember" things. It serves as the immutable configuration for a piece of UI [src/pythra/pythra/state.py43-55](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L43-L55)`State`The "Brain"A persistent object that holds mutable data and logic. It outlives individual `StatefulWidget` instances during reconciliation [src/pythra/pythra/state.py161-168](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L161-L168)`StatelessWidget`The "Poster"A widget that never changes once created, representing static parts of the UI [src/pythra/pythra/state.py104-112](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L104-L112)
#### Entity Relationship and Code Mapping

The following diagram shows how high-level state concepts map to specific class definitions and their lifecycle relationships.

**State System Entity Map**

```

```

Sources: [src/pythra/pythra/state.py43-228](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L43-L228)[src/pythra/pythra/base.py143-145](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L143-L145)

---

### The State Lifecycle

The `State` object undergoes a specific sequence of lifecycle hooks that allow developers to manage resources and respond to tree changes.

1. **`initState()`**: Called exactly once when the state object is first created and inserted into the tree [src/pythra/pythra/state.py183-188](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L183-L188)
2. **`didUpdateWidget(old_widget)`**: Called whenever the widget configuration changes but the `State` object is retained (e.g., during reconciliation when keys match) [src/pythra/pythra/state.py195-200](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L195-L200)
3. **`build()`**: Returns the widget subtree representing this state's current data [src/pythra/pythra/state.py214-220](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L214-L220)
4. **`dispose()`**: Called when the widget is permanently removed from the tree. Used for cleaning up timers or closing sockets [src/pythra/pythra/state.py206-211](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L206-L211)

### Triggering Reconciliation: `setState()`

The `setState()` method is the primary mechanism for updating the UI. When called, it accepts a function (usually a lambda) that modifies the internal variables of the `State` class [src/pythra/pythra/state.py228-235](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L228-L235)

#### Internal Update Flow

Instead of immediately re-rendering the entire application, PyThra uses a queued approach:

1. **Queueing**: The state update is added to the `_pending_state_updates` queue within the `Framework`[src/pythra/pythra/state.py246-248](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L246-L248)
2. **Timer Trigger**: A `QTimer` (single-shot) is started to trigger the reconciliation process on the next event loop tick [src/pythra/pythra/state.py249-251](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L249-L251)
3. **Targeted Subtree Update**: The reconciler processes only the subtree rooted at the `StatefulWidget` that called `setState()`, rather than the whole app tree [src/pythra/pythra/state.py230-232](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L230-L232)

**State Update Pipeline**

```

```

Sources: [src/pythra/pythra/state.py228-251](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L228-L251)[src/pythra/pythra/state.py27-28](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L27-L28)

---

### Implementation Details: `state.py` and `base.py`

#### Widget Identity and Keys

Every `Widget` inherits from the base class in `base.py`, which provides a unique `html_id` and optional `Key`[src/pythra/pythra/base.py143-157](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L143-L157) Keys are essential for state management in lists; they ensure that the `State` object is associated with the correct semantic item even if its index in a list changes [src/pythra/pythra/base.py19-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L19-L35)

#### Framework Integration

`StatefulWidget` maintains a weak reference to the `Framework` instance via `_framework_ref`[src/pythra/pythra/state.py79-83](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L79-L83) This allows the `State` object to notify the orchestrator when it needs a rebuild without creating circular dependencies that would prevent garbage collection.

#### Comparison and Hashing

To optimize updates, PyThra uses `make_hashable` in `base.py` to compare widget properties. This function converts complex style objects (like `EdgeInsets` or `BoxDecoration`) into tuples that can be compared efficiently during the diffing phase [src/pythra/pythra/base.py84-121](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L84-L121)
FunctionFilePurpose`make_hashable(value)``base.py`Converts styles/props to comparable fingerprints [src/pythra/pythra/base.py84-119](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L84-L119)`set_framework(framework)``state.py`Class method to inject the singleton framework reference [src/pythra/pythra/state.py81-83](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L81-L83)`get_state()``state.py`Retrieves the persistent `State` instance from a `StatefulWidget`[src/pythra/pythra/state.py95-97](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L95-L97)
Sources: [src/pythra/pythra/state.py79-97](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L79-L97)[src/pythra/pythra/base.py84-157](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/base.py#L84-L157)