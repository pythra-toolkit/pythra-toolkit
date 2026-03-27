# Pythra Architecture Report: High-Performance Media Player Plugins

This report outlines the architectural roadmap for implementing the **Video Player Widget** and **Audio Player Widget** as defined in `todo.md`. Given that both plugins require `ffmpeg.wasm` to achieve universal codec support purely in the browser, an optimized, decoupled plugin architecture is necessary to prevent redundant memory allocation and massive asset duplication.

---

## 🏗️ 1. Multi-Plugin Architecture (The "Shared Engine" Approach)

Instead of bundling `ffmpeg.wasm` into both the video and audio plugins separately, we should leverage Pythra's new `PackageType` system to create three distinct plugins.

### A. `ffmpeg_core` (Utility Plugin)
- **Type:** `Utility`
- **Purpose:** Acts as a shared foundation. It hosts the massive `ffmpeg.wasm` binary and exposes a global JavaScript API.
- **Assets:** Stores `ffmpeg.js`, `ffmpeg-core.js`, and `ffmpeg-core.wasm` in its `render/vendor/` directory.
- **JS Engine:** Initializes an optimized `window.PythraFFmpegManager` singleton. This ensures `ffmpeg` is only loaded into the browser's RAM once, regardless of how many video/audio players are instantiated.

### B. `video_player` (Widget Plugin)
- **Type:** `Plugin`
- **Dependencies:** Requires `"ffmpeg_core": ">=1.0.0"` in its `package.json`.
- **Purpose:** Provides the Python `VideoPlayer(Widget)` UI. 
- **JS Engine:** Its frontend controller grabs the FFmpeg instance via `window.PythraFFmpegManager`, handles `File.slice()` chunking (or HLS remuxing), and feeds the derived Blob URL into a `<video>` tag.

### C. `audio_player` (Widget Plugin)
- **Type:** `Plugin`
- **Dependencies:** Requires `"ffmpeg_core": ">=1.0.0"`.
- **Purpose:** Provides the Python `AudioPlayer(Widget)` UI.
- **JS Engine:** Similar to the video player, but optimized for extracting audio streams (`-vn`), utilizing the HTML5 `<audio>` API, and potentially rendering WebAudio waveforms.

---

## ⚙️ 2. Critical Pythra Core Modifications

To enable "High-Performance" multi-threaded `ffmpeg.wasm`, modern browsers strictly require **Cross-Origin Isolation** via `SharedArrayBuffer`.

Currently, Pythra's `AssetServer` handles CORS headers, but it lacks the isolation headers. To support these plugins, we must implement a minor architectural upgrade to `src/pythra/pythra/server.py`.

Inside `MultiDirectoryRequestHandler.end_headers()`, the following headers must be appended:
```python
self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
```
*Note: This could also be exposed as an `enable_wasm_multithreading` flag in the Pythra core `config.yaml` to prevent disrupting other standard web behaviors.*

---

## 🚀 3. Asset Management & Path Resolution

One of the greatest benefits of running Pythra locally is that we do not need to fetch the 30MB+ WebAssembly binaries over the internet. 

Based on the recent fixing of Pythra's absolute CSS/JS asset paths, the `ffmpeg_core` plugin will effortlessly serve these massive binaries directly to the browser from the local filesystem:
```javascript
await ffmpeg.load({
    coreURL: `http://localhost:${window.PYTHRA_PORT}/packages/ffmpeg_core/vendor/ffmpeg-core.js`,
    wasmURL: `http://localhost:${window.PYTHRA_PORT}/packages/ffmpeg_core/vendor/ffmpeg-core.wasm`,
});
```
*(The Pythra framework will seamlessly handle requests to `/packages/ffmpeg_core/` via the internal `AssetServer`)*

---

## 🎬 4. High-Performance Execution Flow

By structuring it this way, the flow perfectly maps to the Pythra lifecycle:

1. **Initialization:** User drops a `VideoPlayer` widget into their Python `main.py` UI.
2. **Package Manager:** Pythra strictly loads `ffmpeg_core` before `video_player` due to the dependency resolution graph.
3. **Browser Mount:** The `ffmpeg_core` JS engine provisions global state `window.PythraFFmpegEngine`.
4. **Playback Execution:** The `video_player` Javascript intercepts the internal `<input>` file dialog, invokes `ffmpeg.exec(['-i', file.name, '-c:v', 'copy', '-c:a', 'copy', 'out.mp4'])` via the shared engine, and mounts the fast-remuxed blob stream inside the Pythra DOM tree.

By isolating the heavy encoding/decoding engine as a `Base Utility Plugin`, you ensure the Pythra ecosystem remains deeply modulized, memory-efficient, and easily extensible to audio players or even future image-conversion tools!
