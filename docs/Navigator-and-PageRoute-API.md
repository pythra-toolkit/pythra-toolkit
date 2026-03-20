# Navigator and PageRoute API
Relevant source files
- [CHANGELOG.md](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/CHANGELOG.md)
- [pyproject.toml](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/pyproject.toml)
- [src/pythra/pythra/__init__.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py)
- [src/pythra/pythra/derived_widgets/dropdown/dropdown.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/dropdown.py)
- [src/pythra/pythra/derived_widgets/dropdown/style.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/derived_widgets/dropdown/style.py)
- [src/pythra/pythra/navigation.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py)
- [src/pythra/setup.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/setup.py)

The Navigation system in PyThra provides a stack-based routing model inspired by Flutter. It enables developers to manage application states as a series of pages, supporting standard operations like pushing new routes, popping back to previous views, and advanced performance optimizations like asynchronous preloading.

## Core Navigation Classes

The system is built around three primary entities: the `Navigator` widget, its corresponding `NavigatorState`, and the `PageRoute` definition.

### Navigator (StatefulWidget)

The `Navigator` is a `StatefulWidget` that acts as the container for the navigation stack. It is initialized with an `initialRoute` and an optional dictionary of named routes [src/pythra/pythra/navigation.py79-98](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L79-L98)

### NavigatorState (State)

The `NavigatorState` manages the actual `history` stack (a list of `PageRoute` objects). It provides the imperative API for manipulating the stack, such as `push`, `pop`, and `preload`[src/pythra/pythra/navigation.py38-42](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L38-L42)

### PageRoute

A `PageRoute` encapsulates a `builder` function. This builder is responsible for lazily creating the widget instance that represents the page. It also stores a `widget_instance` once built to support the deferred build pattern [src/pythra/pythra/navigation.py9-14](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L9-L14)
ClassResponsibilityFile Reference`Navigator`Entry point widget for the navigation subtree.[src/pythra/pythra/navigation.py79](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L79-L79)`NavigatorState`Manages the `history` stack and triggers re-renders.[src/pythra/pythra/navigation.py38](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L38-L38)`PageRoute`Defines how a page is constructed and cached.[src/pythra/pythra/navigation.py9](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L9-L9)
## Navigation Flow and Logic

The following diagram illustrates the relationship between the Natural Language concepts of "Moving between screens" and the specific Code Entities that execute those actions.

**Navigation Entity Mapping**

```

```

Sources: [src/pythra/pythra/navigation.py44-77](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L44-L77)

## Deferred Build Pattern (Lazy Loading)

To optimize memory and startup time, `PageRoute` implements a deferred build pattern. The `widget_instance` is not created until the `build()` method is explicitly called by the `NavigatorState`[src/pythra/pythra/navigation.py17-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L17-L20)

1. **Instantiation**: `PageRoute` is created with a `builder` lambda.
2. **First Build**: When the route becomes the top of the stack, `active_route.build(self)` is called.
3. **Caching**: The resulting `Widget` is stored in `self.widget_instance`.
4. **Subsequent Access**: Future calls to `build()` return the cached instance, preserving the internal state of the page's widgets [src/pythra/pythra/navigation.py18-20](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L18-L20)

## Stack Manipulation Methods

The `NavigatorState` provides several methods to control the route history:

### push(route: PageRoute)

Adds a new route to the top of the `history` stack and calls `self.setState()`. This triggers the framework to reconcile the `Navigator` subtree, effectively rendering the new page [src/pythra/pythra/navigation.py44-46](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L44-L46)

### pop()

Removes the top-most route from the stack, provided there is more than one route present. It then calls `self.setState()` to return to the previous view [src/pythra/pythra/navigation.py60-63](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L60-L63)

### preload(route: PageRoute)

Initiates a background build of a route. It calls `route.preload(self)`, which utilizes `Framework.instance().build_subtree_async()` to pre-render the widget tree on a background thread. This ensures that when the user eventually navigates to that page, the HTML stub and state are already prepared [src/pythra/pythra/navigation.py28-35](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L28-L35)[src/pythra/pythra/navigation.py48-50](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L48-L50)

### preloadPrevious()

An optimization specifically for back-navigation. It identifies the route at `history[-2]` and preloads it. This is useful when the user is likely to return to a previous screen that may have been disposed or requires a fresh build [src/pythra/pythra/navigation.py52-58](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L52-L58)

## Data Flow: Navigator to Page

The `NavigatorState` passes itself into the `PageRoute.build` method. This allows the builder function to receive a reference to the `NavigatorState`, enabling child widgets (like buttons on a page) to call `navigator.pop()` or `navigator.push()` without needing a global context lookup [src/pythra/pythra/navigation.py11-12](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L11-L12)[src/pythra/pythra/navigation.py76-77](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L76-L77)

**Route Stack Data Flow**

```

```

Sources: [src/pythra/pythra/navigation.py44-77](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L44-L77)

## Implementation Details

- **Empty Stack Guard**: If the `history` is empty during a build, the Navigator returns a `Container` with an error message to prevent framework crashes [src/pythra/pythra/navigation.py70-72](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L70-L72)
- **State Propagation**: The `PageRoute.setState()` method allows forcing a refresh on the underlying `widget_instance` if it exists [src/pythra/pythra/navigation.py22-25](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L22-L25)
- **Type Hinting**: `NavigatorState` uses string-based type hints (`'NavigatorState'`) in `PageRoute` to handle circular references between the route and the navigator state [src/pythra/pythra/navigation.py11](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L11-L11)

Sources:

- [src/pythra/pythra/navigation.py1-101](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/navigation.py#L1-L101)
- [src/pythra/pythra/__init__.py36](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__init__.py#L36-L36)
- [src/pythra/pythra/state.py1-100](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/state.py#L1-L100) (Context for StatefulWidget/State)