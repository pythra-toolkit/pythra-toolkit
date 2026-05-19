# ResponsiveBuilder Implementation & Performance Analysis

## Overview
The `ResponsiveBuilder` is a powerful adaptive layout widget in PyThra that responds to window resize events with intelligent debouncing and minimal DOM updates. This document details its architecture, performance mechanisms, and optimization strategies.

---

## 1. ResponsiveBuilder Class Definitions

### Location: [src/pythra/pythra/widgets.py](src/pythra/pythra/widgets.py)

#### Modern Implementation (Lines 7444-7530)
```python
class ResponsiveBuilderState(State):
    """State for ResponsiveBuilder that listens for browser viewport resize events.
    
    Resize events originate from a browser-side ResizeObserver on #root-container,
    forwarded via QWebChannel → Api.on_viewport_resize → Framework.handle_resize.
    This guarantees events only fire after the DOM is loaded and the JS-Python
    bridge is connected, eliminating premature setState during window creation.
    """

    def initState(self):
        self.width = self.framework.window_width if self.framework else 0
        self.height = self.framework.window_height if self.framework else 0
        self._resize_timer = None
        self._mounted = True
        self._pending_width = 0
        self._pending_height = 0
        # Safe to register immediately — resize events only arrive from the
        # browser ResizeObserver AFTER the DOM and QWebChannel are ready.
        if self.framework:
            self.framework.register_resize_listener(self._on_resize_raw)

    def dispose(self):
        self._mounted = False
        if self.framework:
            self.framework.unregister_resize_listener(self._on_resize_raw)
        if self._resize_timer:
            self._resize_timer.stop()
            self._resize_timer = None

    def _on_resize_raw(self, width: int, height: int):
        """Raw resize handler with 50ms debounce timer."""
        if not self._mounted:
            return

        from PySide6.QtCore import QTimer

        if not self._resize_timer:
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._apply_resize)

        self._pending_width = width
        self._pending_height = height
        self._resize_timer.start(50)  # 50ms debounce interval

    def _apply_resize(self):
        """Apply resize only if dimensions actually changed."""
        if not self._mounted:
            return
        if self.width != self._pending_width or self.height != self._pending_height:
            self.width = self._pending_width
            self.height = self._pending_height
            self.setState()  # Trigger reconciliation

    def build(self):
        return self.widget.builder(self.width, self.height)

class ResponsiveBuilder(StatefulWidget):
    """
    A widget that rebuilds itself whenever the window is resized.
    
    This acts similarly to Flutter's MediaQuery or LayoutBuilder by providing
    the current window dimensions (width, height) to a builder function.
    """
    def __init__(self, builder: Callable[[int, int], Widget], key: Optional[Key] = None):
        super().__init__(key=key)
        self.builder = builder
        
    def createState(self):
        return ResponsiveBuilderState()
```

#### Legacy Implementation (Lines 72-125)
```python
class ResponsiveBuilderState(State):
    def initState(self):
        from .core import Framework
        framework = Framework.instance()
        self.width = framework.window_width
        self.height = framework.window_height
        self._last_resize_time = 0
        
        # Register listener
        framework.register_resize_listener(self._on_resize)

    def dispose(self):
        from .core import Framework
        framework = Framework.instance()
        framework.unregister_resize_listener(self._on_resize)

    def _on_resize(self, width, height):
        import time
        from PySide6.QtCore import QTimer
        
        self._last_resize_time = time.time()
        
        def check_and_trigger():
            # If 100ms have passed since the last resize event, trigger state update
            if time.time() - self._last_resize_time >= 0.09:
                if self.width != width or self.height != height:
                    self.width = width
                    self.height = height
                    self.setState()
                    
        QTimer.singleShot(100, check_and_trigger)

    def build(self) -> Widget:
        # Return the built widget using current dimensions
        return self.widget.builder(self.width, self.height)

class ResponsiveBuilder(StatefulWidget):
    """
    A widget that rebuilds its child based on the current window dimensions.
    Similar to Flutter's LayoutBuilder or MediaQuery usage, it listens to 
    global window resize events and triggers a rebuild with the new width and height.
    Includes a 100ms debounce to prevent performance degradation during rapid resizing.
    """
    def __init__(self, builder: Callable[[float, float], Widget], key: Optional[Key] = None):
        super().__init__(key=key)
        self.builder = builder

    def createState(self):
        return ResponsiveBuilderState()
```

**Key Differences:**
- Modern version uses **50ms debounce** (better responsiveness)
- Modern version uses **QTimer with pending state** (cleaner implementation)
- Legacy version uses **100ms debounce** (more aggressive debouncing)
- Legacy version uses **time.time() comparison** (manual debounce tracking)

---

## 2. Framework Resize Event Handling

### Location: [src/pythra/pythra/core.py](src/pythra/pythra/core.py)

#### Framework Initialization (Lines 235-250)
```python
# Window Resize Listeners
self._resize_listeners: Set[Callable[[int, int], None]] = set()
self.window_width: int = 0
self.window_height: int = 0

# JS Engine mapping for optimized imports
self._engine_to_file_map = {
    'generateRoundedPath': "render/js/pathGenerator.js",
    'ResponsiveClipPath': "render/js/clipPathUtils.js", 
    'scalePathAbsoluteMLA': "render/js/clipPathUtils.js",
    'PythraSlider': "render/js/slider.js",
    'PythraDropdown': "render/js/dropdown.js",
    'PythraGestureDetector': "render/js/gesture_detector.js",
    'PythraGradientClipPath': "render/js/gradient_border.js",
    'PythraVirtualList': "render/js/virtual_list.js",
    'PythraVirtualGrid': "render/js/virtual_grid.js",
    'PythraTextField': "render/js/textfield.js",
    'PythraVirtualizedDropdownInternal': "render/js/virtual_dropdown.js"
}
```

#### Resize Listener Methods (Lines 304-320)
```python
def register_resize_listener(self, listener: Callable[[int, int], None]):
    """Register a callback for window resize events."""
    self._resize_listeners.add(listener)

def unregister_resize_listener(self, listener: Callable[[int, int], None]):
    """Unregister a window resize callback."""
    if listener in self._resize_listeners:
        self._resize_listeners.remove(listener)

def handle_resize(self, width: int, height: int):
    """Notify all registered listeners about a window resize.
    
    This is called from the browser via QWebChannel when the ResizeObserver
    detects viewport changes. It updates the Framework's window dimensions
    and notifies all registered listeners in sequence.
    """
    self.window_width = width
    self.window_height = height
    for listener in list(self._resize_listeners):
        listener(width, height)
```

**Design Pattern: Observer Pattern**
- Framework maintains a set of resize listeners
- Each ResponsiveBuilderState registers itself as a listener on init
- On dispose, unregisters to prevent memory leaks
- Listeners are called in sequence with new dimensions

---

## 3. Performance Profiling & Monitoring

### Location: [src/pythra/pythra/core.py](src/pythra/pythra/core.py) Lines 990-1010

```python
def _process_reconciliation(self):
    #...existing code...
    
    print(f"🎉 PyThra Framework | UI Update Complete! at (⏱️ {cycle_duration:.4f}s) ({(cycle_duration * 1000):.2f}ms) ({fps:.2f} FPS)")

    if profiler and is_debug:
        profiler.disable()
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)
        print("\n--- cProfile Report ---")
        print(s.getvalue())
        print("--- End of Report ---\n")
```

**Performance Metrics Tracked:**
- Cycle duration in seconds (`cycle_duration`)
- Cycle duration in milliseconds
- Frames per second (FPS)
- Top 20 cumulative time functions (when debug enabled)

**Debug Flag Control:**
- Performance profiling only runs when `is_debug=True`
- cProfile provides detailed call stack analysis
- Output shows cumulative time spent in each function

---

## 4. Browser-Side ResponsiveClipPath (JavaScript)

### Location: [src/pythra/pythra/render/js/clipPathUtils.js](src/pythra/pythra/render/js/clipPathUtils.js)

#### ResizeObserver Implementation (Lines 233-260)
```javascript
export class ResponsiveClipPath {
  constructor(target, originalPath, refW, refH, options = {}) {
    this.elements = [];
    this.orig = originalPath.trim();
    this.refW = refW;
    this.refH = refH;
    this.options = options;
    this.currentPath = "";  // ⬅️ Store last computed path string
    this.update = this.update.bind(this);
    this.roList = [];

    this.isClassSelector = typeof target === 'string' && target.startsWith('.');
    this.selector = target;
    this.styleTagId = this.isClassSelector ? `clip-style-${target.substring(1)}` : null;

    if (this.isClassSelector) {
      let styleTag = document.getElementById(this.styleTagId);
      if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = this.styleTagId;
        document.head.appendChild(styleTag);
      }
      this.styleTag = styleTag;
    }

    if (typeof target === 'string') {
      let selector = target;
      if (!selector.startsWith('#') && !selector.startsWith('.')) {
        const byId = document.getElementById(selector);
        selector = byId ? `#${selector}` : `.${selector}`;
      }
      const nodeList = document.querySelectorAll(selector);
      if (nodeList.length === 0) {
        console.warn(`ResponsiveClipPath: no elements found for selector "${selector}"`);
      }
      nodeList.forEach(el => this.elements.push(el));
    } else if (target instanceof HTMLElement) {
      this.elements.push(target);
    } else {
      console.warn('ResponsiveClipPath: invalid target', target);
    }

    if (this.isClassSelector) {
      this.observeRepresentative();
    } else {
      this.elements.forEach(el => this.initElement(el));
    }
  }

  initElement(el) {
    this.applyClip(el);
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => this.applyClip(el));
      ro.observe(el);
      this.roList.push({ el, ro });
    } else {
      window.addEventListener('resize', this.update);
    }
  }

  applyClip(el) {
    const rect = el.getBoundingClientRect();
    // Recalculate clip-path based on current element dimensions
    const newPath = scalePathAbsoluteMLA(
      this.orig,
      this.refW,
      this.refH,
      rect.width,
      rect.height,
      this.options
    );
    this.currentPath = `path("${newPath}")`;  // ⬅️ Save it
    el.style.clipPath = this.currentPath;
    el.style.webkitClipPath = this.currentPath;
  }

  update() {
    if (this.isClassSelector) {
      this.applyClassClip();
    } else {
      this.elements.forEach(el => this.applyClip(el));
    }
  }

  disconnect() {
    this.roList.forEach(({ el, ro }) => ro.unobserve(el));
    this.roList = [];
    window.removeEventListener('resize', this.update);

    if (this.classRo) {
      this.classRo.disconnect();
      this.classRo = null;
    }

    if (this.styleTag && this.styleTag.parentNode) {
      this.styleTag.parentNode.removeChild(this.styleTag);
    }
  }

  getResponsivePath() {
    return this.currentPath;
  }
}
```

**Performance Features:**
- Uses `ResizeObserver` API for efficient resize tracking
- Falls back to `window.addEventListener('resize')` for older browsers
- Caches computed clip-path in `currentPath`
- Properly cleans up observers in `disconnect()` to prevent memory leaks

---

## 5. Animation & Rendering Loops

### CSS Animation Files

#### Loader Animations: [src/pythra/pythra/render/loaders/dots.css](src/pythra/pythra/render/loaders/dots.css)
- Uses CSS `@keyframes` for smooth 60fps animations
- Employs `animation: steps()` for precise control
- Utilizes `clip-path: inset()` for efficient rendering

#### Animation Collection: [src/pythra/pythra/render/anicollection.css](src/pythra/pythra/render/anicollection.css)
- Comprehensive animation library with timing functions
- Uses `cubic-bezier()` for natural motion curves
- Supports configurable animation delays and iteration counts

**CSS Animation Performance Optimizations:**
```css
/* Example: Efficient loader animation using clip-path */
.loader-dots-1 {
  width: 60px;
  aspect-ratio: 4;
  background: radial-gradient(circle closest-side, var(--loader-color, #000) 90%, #0000) 0/calc(100%/3) 100% space;
  clip-path: inset(0 100% 0 0);
  animation: l1 1s steps(4) infinite;
}

@keyframes l1 {
  to {
    clip-path: inset(0 -34% 0 0)
  }
}
```

**Benefits:**
- GPU-accelerated animations
- Minimal repaints through use of `clip-path` and `transform`
- Deterministic frame timing with `steps()`

---

## 6. Event Handlers & Update Mechanisms

### Python Event Flow
```
Browser ResizeObserver
    ↓
JavaScript resize event → QWebChannel → Api.on_viewport_resize()
    ↓
Framework.handle_resize(width, height)
    ↓
For each registered listener in _resize_listeners:
    ↓
ResponsiveBuilderState._on_resize_raw(width, height)
    ↓
QTimer(50ms debounce) → _apply_resize()
    ↓
setState() if dimensions changed
    ↓
ResponsiveBuilderState.build() → builder(width, height)
    ↓
PyThra Reconciler (Diffing Engine)
    ↓
Generate minimal DOM patches
    ↓
Send patches to browser via QWebChannel
    ↓
Browser applies patches to live DOM
```

### Update Mechanism Details

#### ResponsiveBuilderState Update Flow
1. **Event Capture**: `_on_resize_raw()` receives raw resize event
2. **Debounce Timer**: QTimer scheduled for 50ms
3. **Pending State**: New dimensions stored in `_pending_width`, `_pending_height`
4. **Comparison Check**: Only update if dimensions actually changed
5. **State Update**: `setState()` triggers reconciliation
6. **Builder Invocation**: `build()` calls user's builder function
7. **Reconciliation**: Framework diffs new tree against old tree
8. **DOM Patching**: Minimal changes sent to browser

---

## 7. Performance Notes & TODOs

### Documented Best Practices (From [docs/responsive_builder.md](docs/responsive_builder.md))

#### Debouncing Strategy
- **Modern Implementation**: 50ms debounce (responsive)
- **Legacy Implementation**: 100ms debounce (aggressive)
- **Why**: Prevents performance degradation during rapid resize events
- **How**: QTimer delays state update until resize sequence stabilizes

#### Widget Key Requirements
```python
# ✅ CORRECT: Always use stable keys for stateful children
ResponsiveBuilder(
    key=Key("responsive_section"),
    builder=lambda w, h: Column(
        children=[
            VideoPlayer(key=Key("video"), video_path="/video.mp4"),
            TextField(key=Key("input"), placeholder="Type here...")
        ]
    )
)

# ❌ AVOID: No keys on stateful widgets
ResponsiveBuilder(
    builder=lambda w, h: Column(
        children=[
            VideoPlayer(video_path="/video.mp4"),  # Will be recreated on resize!
            TextField(placeholder="Type here...")
        ]
    )
)
```

#### Nesting Strategy
```python
# ✅ GOOD: Place ResponsiveBuilder near changing elements
scaffold = Scaffold(
    body=ResponsiveBuilder(
        builder=lambda w, h: Row() if w > 600 else Column()
    )
)

# ❌ AVOID: Wrapping entire app in ResponsiveBuilder
app = ResponsiveBuilder(
    builder=lambda w, h: Scaffold(
        appBar=AppBar(...),
        body=PageContent(...),
        drawer=Drawer(...)
    )
)
```

#### Pure Builder Functions
- Do NOT mutate global state inside the builder
- Do NOT call API endpoints in the builder
- Only construct and return widgets
- Side effects should be in StatefulWidget lifecycle methods (initState, dispose, etc.)

---

## 8. Performance Bottlenecks & Mitigation

### Potential Issues

1. **Excessive Reconciliation**
   - Problem: Every pixel of resize triggers rebuild
   - Solution: 50ms debounce in modern implementation
   - Status: ✅ Addressed

2. **Widget State Loss**
   - Problem: Stateful widgets recreated on resize
   - Solution: Assign stable Keys to maintain state
   - Status: ⚠️ User responsibility

3. **Deep Nesting Overhead**
   - Problem: Entire UI tree rebuilds on resize
   - Solution: Place ResponsiveBuilder strategically
   - Status: ⚠️ User responsibility

4. **Memory Leaks**
   - Problem: Resize listeners not cleaned up on unmount
   - Solution: dispose() unregisters listeners
   - Status: ✅ Addressed

5. **Browser Memory (ResizeObserver)**
   - Problem: Multiple observers on same element
   - Solution: ResponsiveClipPath.disconnect() cleans up
   - Status: ✅ Addressed

---

## 9. File Summary

| File | Purpose | Key Features |
|------|---------|--------------|
| [src/pythra/pythra/widgets.py](src/pythra/pythra/widgets.py) | ResponsiveBuilder class | Stateful widget with resize debounce |
| [src/pythra/pythra/core.py](src/pythra/pythra/core.py) | Framework resize handling | Observer pattern, listener registration |
| [docs/responsive_builder.md](docs/responsive_builder.md) | User documentation | Examples, best practices, architecture |
| [src/pythra/pythra/render/js/clipPathUtils.js](src/pythra/pythra/render/js/clipPathUtils.js) | Browser ResizeObserver | Efficient clip-path scaling |
| [src/pythra/pythra/render/anicollection.css](src/pythra/pythra/render/anicollection.css) | CSS animations | GPU-accelerated animations |
| [src/pythra/pythra/render/loaders/dots.css](src/pythra/pythra/render/loaders/dots.css) | Loading animations | Efficient clip-path-based loaders |

---

## 10. Key Metrics & Constants

| Metric | Value | Context |
|--------|-------|---------|
| Modern Debounce | 50ms | QTimer interval for resize batching |
| Legacy Debounce | 100ms | Older time.time() based debounce |
| Browser ResizeObserver | Native API | Fallback to window.resize for older browsers |
| cProfile Report | Top 20 functions | Debug mode performance analysis |
| FPS Calculation | Real-time | Displayed in console during updates |

