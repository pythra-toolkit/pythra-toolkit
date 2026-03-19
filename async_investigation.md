# Evaluating Flutter-like Async Patterns for Pythra

Currently, Pythra developers must manually bridge background threads to the main Qt thread using `QTimer.singleShot()`. While functional, this exposes the underlying Qt framework and breaks the seamless, declarative aesthetic of a Flutter-like framework where async behavior is usually handled natively by Dart's event loop or widgets like `FutureBuilder`.

Here is an investigation into ways we could implement a more **Flutter-idiomatic approach** to asynchronous operations in Pythra.

---

## 1. The `FutureBuilder` Widget (Most Flutter-like)
Flutter developers rely heavily on `FutureBuilder` to decouple async state management from the main `State` logic. Pythra could provide a `FutureBuilder` widget that natively spins up a thread and automatically handles the `QTimer` main-thread dispatching internally.

**Developer Experience:**
```python
class MyWidgetState(State):
    def fetch_data(self):
        # Heavy blocking call
        return requests.get("https://api.example.com/data").json()

    def build(self):
        return FutureBuilder(
            future=self.fetch_data,  # Pass a callable (or a Python Future/Task)
            builder=lambda context, snapshot: (
                ProgressIndicator() if snapshot.connectionState == ConnectionState.WAITING
                else Text(f"Result: {snapshot.data}")
            )
        )
```

**Pros:** 
- Extremely familiar to Flutter developers. 
- Fully encapsulates the thread pool and the `QTimer` dispatching.
- Keeps the `build()` method incredibly declarative.

---

## 2. A Built-in `State.run_async()` Helper
Instead of asking developers to import `threading` and `QTimer`, Pythra's `State` class could expose a simple helper method to handle the heavy lifting.

**Developer Experience:**
```python
class PromptToolState(State):
    def submit(self):
        self.loader_ctrl.show()
        
        # Framework cleanly handles thread creation and Qt bridging
        self.run_async(
            task=self._do_request,      # Runs in a background thread
            on_done=self._finish        # Safely runs on the main UI thread afterwards
        )

    def _do_request(self):
        return requests.post("...").text

    def _finish(self, reply):
        self.output_ctrl.text = reply
        self.loader_ctrl.hide()
```

**Pros:** 
- No complex widget logic. Very easy to implement. 
- Completely hides Qt imports like `QTimer` and `threading` from the developer's code.

---

## 3. UI Thread Decorators
We could provide intuitive decorators like `@background_task` and `@ui_thread` to marshal execution automatically.

**Developer Experience:**
```python
from pythra.async_utils import background_task, ui_thread

class PromptToolState(State):
    @background_task
    def submit(self):
        # ... heavy data fetching ...
        reply = requests.post("...").text
        self._finish(reply)
        
    @ui_thread # Automatically uses QTimer.singleShot under the hood
    def _finish(self, reply):
        self.output_ctrl.text = reply
        self.loader_ctrl.hide()
```

**Pros:** Pythonic and clean. Focuses purely on the business logic.

---

## 4. Native `async/await` Support (The `qasync` Integration)
In Flutter/Dart, asynchronous UI updates are seamless because Dart's event loop handles futures naturally—you just `await` and then call `setState()`. 

By integrating the `qasync` library (an `asyncio` event loop built on top of Qt), Pythra could support native Python async functions directly in the UI thread.

**Developer Experience:**
```python
class PromptToolState(State):
    async def submit(self):
        self.loader_ctrl.show()
        self.setState()
        
        # 'await' yields control to the Qt event loop natively!
        reply = await self.fetch_data_from_openai() 
        
        self.output_ctrl.text = reply
        self.loader_ctrl.hide()
        self.setState() # Safe on the main thread!
```

**Pros:** The exact same aesthetic as Dart's `async/await`. No callback hell.
**Cons:** Requires the `qasync` dependency. Users must learn Python `asyncio` (e.g., synchronous `requests` calls will block the whole app unless passed through `await asyncio.to_thread()`, which introduces complexity).

---

## Conclusion

To regain the "Flutter aesthetic" without throwing Python's strengths away, I recommend a dual approach:

1. **Short-Term Quick Win:** Implement a `FutureBuilder` widget and/or a `self.run_async()` wrapper inside `State`. This gives an immediate, Qt-free API for developers that naturally masks thread-handling boilerplate, fulfilling the declarative promises of the framework without risking major runtime crashes.
2. **Long-Term Evolution:** Investigate the feasibility of `qasync` to allow native `async def _onPressed(self)` callbacks. This brings Python's modern `asyncio` patterns directly into Pythra, exactly mirroring Dart's async model.
