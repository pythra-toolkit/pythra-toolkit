// pythra_ffmpeg_core/render/js/ffmpeg_engine.js
// Pythra High-Performance Shared FFmpeg WebAssembly Manager
// Uses the Emscripten-compiled createFFmpegCore directly (non-threaded, no worker needed)

class PythraFFmpegManager {
    constructor() {
        this.status = 'uninitialized';
        this.core = null; // The resolved Emscripten Module (createFFmpegCore result)
    }

    async loadEngine() {
        if (this.status === 'loaded' || this.status === 'loading') {
            return;
        }

        this.status = 'loading';
        console.log("[PythraFFmpegManager] Allocating ffmpeg.wasm binaries into browser memory...");

        try {
            // createFFmpegCore is defined globally by ffmpeg-core.js (Emscripten IIFE build)
            if (typeof createFFmpegCore === 'undefined') {
                throw new Error("createFFmpegCore is not defined! Ensure ffmpeg-core.js was loaded by Pythra.");
            }

            // Resolve the pythra asset server port defined natively
            const port = window.__PYTHRA_CONFIG__ ? window.__PYTHRA_CONFIG__.assets_server_port : 8000;
            const baseUrl = `http://localhost:${port}/packages/pythra_ffmpeg_core/vendor/ffmpeg`;

            // Initialize the Emscripten module, pointing it at the served .wasm file.
            // IMPORTANT: createFFmpegCore(config) returns the ready Promise directly.
            //
            // We cannot use `locateFile` here because Emscripten computes wasmBinaryFile
            // BEFORE Object.assign() restores our override. Instead we use the dedicated
            // `mainScriptUrlOrBlob` mechanism: _locateFile() checks Module["mainScriptUrlOrBlob"]
            // FIRST (it's still on Module when _locateFile runs), decodes the fragment as
            // base64(JSON({ wasmURL, workerURL })) and returns the correct URL.
            const wasmUrl = `${baseUrl}/ffmpeg-core.wasm`;
            const encoded = btoa(JSON.stringify({ wasmURL: wasmUrl, workerURL: '' }));
            this.core = await createFFmpegCore({
                mainScriptUrlOrBlob: `pythra-ffmpeg#${encoded}`
            });

            this.status = 'loaded';
            console.log("✅ [PythraFFmpegManager] FFmpeg Engine Successfully Mounted internally!");
        } catch (err) {
            console.error("❌ [PythraFFmpegManager] Failed to mount engine:", err);
            this.status = 'error';
            throw err;
        }
    }

    async processMedia(inputFileData, inputFileName, ffmpegArgs) {
        if (this.status !== 'loaded') {
            await this.loadEngine();
        }

        try {
            // Write input file to Emscripten's in-memory filesystem (FS)
            this.core.FS.writeFile(inputFileName, inputFileData);

            console.log(`[PythraFFmpegManager] Executing: ffmpeg ${ffmpegArgs.join(' ')}`);

            // Run ffmpeg with the provided args
            // The Emscripten build exposes exec(...args) directly via Module
            this.core.exec(...ffmpegArgs);

            console.log(`[PythraFFmpegManager] Execution complete.`);
            return true;
        } catch (err) {
            console.error(`[PythraFFmpegManager] Execution Error:`, err);
            return false;
        }
    }

    async readOutput(outputFileName) {
        if (this.status !== 'loaded' || !this.core) return null;
        try {
            return this.core.FS.readFile(outputFileName);
        } catch (err) {
            console.warn(`[PythraFFmpegManager] Failed to read output file ${outputFileName}:`, err);
            return null;
        }
    }

    async removeFile(fileName) {
        try {
            if (this.status === 'loaded' && this.core) {
                this.core.FS.unlink(fileName);
            }
        } catch(e) {
            console.warn(`[PythraFFmpegManager] Failed to delete file ${fileName} from memfs.`, e);
        }
    }
}

// Map the Pythra FFmpeg Engine to Window globally
if (typeof window.PythraFFmpegManagerInstance === 'undefined') {
    window.PythraFFmpegManagerInstance = new PythraFFmpegManager();
}
