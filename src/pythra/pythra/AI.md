# Building AI-Powered Applications with Pythra

Pythra's Flutter-inspired architecture makes it a natural fit for AI-powered desktop applications.
Its reactive state system, plugin pipeline, and direct Python-to-JS bridge let you wire any AI model
or API directly into your UI without fighting a separate frontend layer.

This guide shows how Pythra's primitives map to three real-world AI use cases:
**AI tools**, **AI editors**, and **AI dashboards**.

---

## Core Patterns Used Across All AI Apps

Before diving into each category, understand the three Pythra patterns you will use everywhere.

### 1. Async-safe State Updates with `QTimer`

AI calls (HTTP requests, model inference, streaming) happen off the main thread.
Pythra's UI must be updated from the main Qt thread.
Use `QTimer.singleShot(0, callback)` to safely dispatch any state change back to the UI.

```python
from PySide6.QtCore import QTimer

class MyAIState(State):
    def initState(self):
        self.is_loading = False
        self.result = ""

    def run_ai(self):
        self.is_loading = True
        self.setState()                          # show spinner immediately
        QTimer.singleShot(0, self._call_model)  # defer heavy work safely

    def _call_model(self):
        import requests
        response = requests.post("https://api.example.com/generate", json={...})
        self.result = response.json()["text"]
        self.is_loading = False
        self.setState()                          # update UI on the main thread
```

### 2. Controllers as the AI ↔ Widget Bridge

Controllers let you talk to widgets programmatically — inject model output into a field,
reset a progress indicator, or clear a text area — without rebuilding the whole tree.

```python
output_controller = TextEditingController(text="")

# Anywhere in your State: push model output into the TextField
output_controller.text = model_response   # triggers listener, updates UI
```

### 3. `ProgressIndicatorController` for Loading States

Swap a spinner in and out without rebuilding the parent widget.

```python
from pythra import ProgressIndicator, ProgressIndicatorController, Loader, LoaderStyle

loader_ctrl = ProgressIndicatorController(visible=False)

# Show on AI call start
loader_ctrl.show()

# Hide when done
loader_ctrl.hide()

# In build():
ProgressIndicator(
    controller=loader_ctrl,
    loader=Loader.BARS,
    style=LoaderStyle.LOADER_BARS_1,
)
```

---

## 1. AI Tools

An **AI tool** is a focused utility — a prompt runner, code explainer, image analyzer,
translation widget, summarizer, etc. It takes input, calls a model, and displays output.

### Architecture

```
TextField (input)
    └─► ElevatedButton (onPressed → State.run_ai())
            └─► [AI API call via requests / openai / etc.]
                    └─► TextEditingController → TextField (output)
```

### Minimal Example — Prompt Runner

```python
from pythra import (
    Framework, StatefulWidget, State,
    Scaffold, Column, Row, TextField, ElevatedButton,
    Text, SizedBox, Key, InputDecoration, TextEditingController,
    ProgressIndicator, ProgressIndicatorController, Loader, LoaderStyle,
    Colors, EdgeInsets, MainAxisAlignment, CrossAxisAlignment,
)
from PySide6.QtCore import QTimer
import threading, requests

class PromptToolState(State):
    def initState(self):
        self.prompt_ctrl  = TextEditingController()
        self.output_ctrl  = TextEditingController()
        self.loader_ctrl  = ProgressIndicatorController(visible=False)

    def _do_request(self):
        """Runs in a background thread."""
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer YOUR_KEY"},
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": self.prompt_ctrl.text}],
                },
                timeout=30,
            )
            reply = r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Error: {e}"

        # Schedule UI update back on Qt main thread
        QTimer.singleShot(0, lambda: self._finish(reply))

    def _finish(self, reply: str):
        self.output_ctrl.text = reply
        self.loader_ctrl.hide()

    def submit(self):
        if not self.prompt_ctrl.text.strip():
            return
        self.loader_ctrl.show()
        threading.Thread(target=self._do_request, daemon=True).start()

    def build(self):
        return Scaffold(
            body=Column(
                key=Key("prompt_col"),
                mainAxisAlignment=MainAxisAlignment.START,
                children=[
                    TextField(
                        key=Key("prompt_input"),
                        controller=self.prompt_ctrl,
                        decoration=InputDecoration(label="Your prompt"),
                    ),
                    SizedBox(height=8, key=Key("gap1")),
                    ElevatedButton(
                        key=Key("submit_btn"),
                        child=Text("Run", key=Key("submit_txt")),
                        onPressed=self.submit,
                    ),
                    SizedBox(height=8, key=Key("gap2")),
                    ProgressIndicator(
                        key=Key("loader"),
                        controller=self.loader_ctrl,
                        loader=Loader.BARS,
                        style=LoaderStyle.LOADER_BARS_1,
                    ),
                    TextField(
                        key=Key("output_field"),
                        controller=self.output_ctrl,
                        decoration=InputDecoration(label="Output"),
                    ),
                ],
            ),
        )

class PromptTool(StatefulWidget):
    def createState(self): return PromptToolState()

app = Framework.instance()
app.set_root(PromptTool(key=Key("root")))
app.run(title="AI Prompt Tool")
```

### Real-World Extension Points

| Feature | Pythra primitive |
|---|---|
| Model selector | `Dropdown` + `DropdownController` |
| Temperature / max-tokens knob | `Slider` + `SliderController` |
| Streaming output | Update `TextEditingController.text` inside a `QTimer` loop |
| Conversation history | `VirtualListView` + `VirtualListController.refresh()` |
| Copy-to-clipboard action | `IconButton` → `framework.window.evaluate_js(...)` |

---

## 2. AI Editors

An **AI editor** embeds AI actions directly inside a rich editing surface —
generation, rewriting, summarizing, translation — all operating on the document selection.

The Note-app included in this repository is a working example: it embeds a
`MarkdownEditor` (plugin), an `AiActionsControls` toolbar, and a floating chat panel,
all wired together through Pythra's state and controller system.

### Architecture

```
MarkdownEditor (plugin widget)          ← owns the document
    └─► MarkdownEditorController        ← programmatic editing API
AiActionsControls (StatefulWidget)      ← mode/action dropdowns + Generate button
    └─► Dropdown (mode: Funny, Formal…)
    └─► Dropdown (action: Summarize, Expand…)
    └─► ElevatedButton → State.generate()
            └─► [AI call]
                    └─► controller.replace_selection_with_markdown(result)
```

### Key Pattern — Overlay AI Controls on an Editor

```python
self.editor = MarkdownEditorController(initial_content="<p>Start here</p>")

self.markdown_editor = MarkdownEditor(
    key=Key("editor"),
    controller=self.editor,
    overlay=AiActionsControls(          # floats above the editor surface
        key=Key("ai_controls"),
        editor=self.editor,             # controller reference passed in
        onGenerate=lambda: self.editor.hide_overlay(),
    ),
)
```

### Writing AI Output Back into the Document

```python
def _finish_generation(self):
    self.is_loading = False
    self.setState()

    generated = call_my_model(
        action=self.action_to_perform["action"],
        mode=self.action_to_perform["mode"],
        selection=self.editor.export_to_markdown(),
    )
    self.editor.replace_selection_with_markdown(generated)
```

### Editor AI Capability Checklist

| Capability | How to implement |
|---|---|
| Operate on selection only | `controller.export_to_markdown()` before AI call |
| Insert image from model | `controller.insert_image(url)` |
| Change font / heading | `controller.set_font_name()`, `controller.set_heading()` |
| Context-aware chat | Pass `export_to_markdown()` as system context to chat panel |
| Custom toolbar buttons | Subclass `MarkdownToolbarItem`, implement `build_widget()` |

### Extending the Toolbar with Custom AI Buttons

Pythra's plugin system lets you add new toolbar items without modifying core code.

```python
# plugins/my_ai_plugin/toolbar.py
from pythra.plugins import MarkdownToolbarItem
from pythra import IconButton, Icon, Icons, ButtonStyle

class SummarizeToolbarItem(MarkdownToolbarItem):
    def build_widget(self, controller):
        return IconButton(
            icon=Icon(Icons.summarize_rounded),
            tooltip="AI Summarize",
            onPressed=lambda: controller.execCommand("summarize"),
            style=ButtonStyle(backgroundColor="transparent"),
        )
```

---

## 3. AI Dashboards

An **AI dashboard** displays live or computed data — metrics, charts, model outputs,
alerts — and lets the user interact with it in real time.

### Architecture

```
Scaffold
├─ AppBar (title, model selector, theme toggle)
└─ body: Row
     ├─ Sidebar: VirtualListView (metric cards)
     └─ Main: Column
          ├─ MetricCard (StatefulWidget)  ← auto-refreshing stat
          ├─ ChartWidget (Container + custom CSS/JS)
          └─ AlertFeed (VirtualListView)
```

### Auto-Refreshing Metric Card

Use `QTimer` to poll an endpoint at a fixed interval and push values to the UI.

```python
from PySide6.QtCore import QTimer

class MetricCardState(State):
    def initState(self):
        self.value = "—"
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(5000)  # refresh every 5 seconds

    def _refresh(self):
        import requests
        try:
            data = requests.get("https://your-ai-backend/metrics").json()
            self.value = str(data["accuracy"])
        except Exception:
            self.value = "error"
        self.setState()

    def dispose(self):
        self._timer.stop()  # always clean up timers

    def build(self):
        return Container(
            key=Key("metric_card"),
            padding=EdgeInsets.all(16),
            child=Column(
                key=Key("metric_col"),
                children=[
                    Text(self.widget.label, key=Key("metric_label"),
                         style=TextStyle(fontSize=14, color=Colors.grey)),
                    Text(self.value, key=Key("metric_value"),
                         style=TextStyle(fontSize=32, fontWeight="bold")),
                ],
            ),
            decoration=BoxDecoration(
                borderRadius=BorderRadius.circular(12),
                color=Colors.adaptive(dark="#1e1e1e", light=Colors.white),
            ),
        )
```

### VirtualListView for Large AI Output Feeds

When your model produces many results (search results, log lines, anomaly alerts),
render them efficiently with `VirtualListView`.

```python
from pythra import VirtualListView, VirtualListController

self.feed_ctrl = VirtualListController()
self.alerts    = []   # populated by AI backend

def on_new_alert(alert_text: str):
    self.alerts.append(alert_text)
    self.feed_ctrl.refresh()  # incremental re-render, no full rebuild

VirtualListView(
    key=Key("alert_feed"),
    controller=self.feed_ctrl,
    itemCount=len(self.alerts),
    itemBuilder=lambda index: AlertCard(text=self.alerts[index]),
    itemHeight=64,
)
```

### Dashboard Layout Patterns

| Pattern | Pythra widgets |
|---|---|
| Side-by-side panels | `Row` + `Expanded` |
| Scrollable card grid | `VirtualGridView` + `VirtualGridController` |
| Floating action menu | `Stack` + `Positioned` + `FloatingActionButton` |
| Global alerts | `SnackBar` + `State.openSnackBar()` |
| Full-screen detail view | `Navigator.push(PageRoute(...))` |
| Theme toggle (dark/light) | `Framework.instance().set_theme(ThemeData(...))` |

### Injecting Custom Chart JS

For charts (line charts, bar charts, pie charts), inject a JS charting library
via the plugin system and communicate with it through `framework.window.evaluate_js`.

```python
# In your State:
def update_chart(self, new_data: list):
    data_json = json.dumps(new_data)
    script = f"window.myChart.data.datasets[0].data = {data_json}; window.myChart.update();"
    Framework.instance().window.evaluate_js(Framework.instance().id, script)
```

Load the chart library (Chart.js, Recharts, etc.) as a plugin JS module:

```json
// plugins/charts_plugin/package.json
{
  "name": "charts_plugin",
  "js_modules": {
    "ChartJS": "assets/chart.umd.min.js"
  }
}
```

---

## Putting It All Together

Pythra gives you everything you need to build production-grade AI applications on the desktop:

| Need | Pythra solution |
|---|---|
| Reactive UI | `StatefulWidget` + `State.setState()` |
| Background AI calls | `threading.Thread` + `QTimer.singleShot` |
| Rich text editing + AI | `MarkdownEditor` plugin + `MarkdownEditorController` |
| Live data polling | `QTimer` in `initState`, stopped in `dispose` |
| Large result lists | `VirtualListView` / `VirtualGridView` |
| Custom JS components | Plugin system + `evaluate_js` bridge |
| Multi-screen navigation | `Navigator` + `PageRoute` |
| Theming | `Framework.instance().set_theme(ThemeData(...))` |

Because Pythra apps are plain Python, you can import **any** AI library —
`openai`, `anthropic`, `transformers`, `langchain`, `llama-cpp-python`, `whisper`,
`opencv-python` — and connect it directly to your widget tree with no adapter layer.
