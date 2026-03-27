window.PythraVideoPlayer = class PythraVideoPlayer {
    constructor(elementOrId, options) {
        this.elementOrId = elementOrId;
        this.options = options;
        this.instanceId = options.instanceId || Math.random().toString(36).substr(2, 9);
        
        setTimeout(() => this.init(), 0);
    }
    
    init() {
        this.container = typeof this.elementOrId === 'string' 
            ? document.getElementById(this.elementOrId) 
            : this.elementOrId;
            
        if (!this.container) return;
        
        // Build the basic interface
        this.container.innerHTML = `
            <div class="pythra-video-player-ui">
                <div class="pythra-video-player-controls" id="controls-${this.instanceId}">
                    <label class="pythra-video-player-upload">
                        Open Video File
                        <input type="file" id="upload-${this.instanceId}" accept="video/*,.mkv,.avi,.flv" style="display:none;">
                    </label>
                    <div class="pythra-video-player-status" id="status-${this.instanceId}">Waiting for file...</div>
                </div>
                <video id="video-${this.instanceId}" class="pythra-video-player-video hidden" controls ${(this.options.auto_play) ? 'autoplay' : ''}></video>
            </div>
        `;

        this.uploader = this.container.querySelector(`#upload-${this.instanceId}`);
        this.statusText = this.container.querySelector(`#status-${this.instanceId}`);
        this.videoEl = this.container.querySelector(`#video-${this.instanceId}`);
        this.controlsEl = this.container.querySelector(`#controls-${this.instanceId}`);

        this.uploader.addEventListener('change', (e) => this.handleUpload(e));
    }

    async handleUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        this.statusText.innerText = `Preparing ${file.name}...`;

        // Retrieve the FFmpeg utility instance provided by `pythra_ffmpeg_core`
        const ffmpegManager = window.PythraFFmpegManagerInstance;
        if (!ffmpegManager) {
            this.statusText.innerText = "Error: pythra_ffmpeg_core dependency missing!";
            return;
        }

        this.statusText.innerText = "Mounting FFmpeg engine...";
        try {
            await ffmpegManager.loadEngine();
        } catch(err) {
            this.statusText.innerText = "Error mounting engine.";
            return;
        }

        const fileData = new Uint8Array(await file.arrayBuffer());
        
        // Setup progress tracking via the Emscripten core module
        if (ffmpegManager.core && ffmpegManager.core.setProgress) {
            ffmpegManager.core.setProgress(({ ratio }) => {
                if (ratio >= 0 && ratio <= 1) {
                    this.statusText.innerText = `Processing: ${Math.round(ratio * 100)}%`;
                }
            });
        }

        this.statusText.innerText = "Attempting fast remux (container swap)...";
        let success = await ffmpegManager.processMedia(fileData, file.name, ['-i', file.name, '-c:v', 'copy', '-c:a', 'copy', `out_${this.instanceId}.mp4`]);
        
        if (!success) {
            this.statusText.innerText = "Fast remux failed, attempting full transcode (this may take a while)...";
            success = await ffmpegManager.processMedia(fileData, file.name, ['-i', file.name, `out_${this.instanceId}.mp4`]);
        }

        if (success) {
             this.statusText.innerText = "Assembling media stream...";
             const data = await ffmpegManager.readOutput(`out_${this.instanceId}.mp4`);
             if (data) {
                 const videoBlob = new Blob([data.buffer], { type: 'video/mp4' });
                 const videoUrl = URL.createObjectURL(videoBlob);
                 
                 this.videoEl.src = videoUrl;
                 this.videoEl.classList.remove('hidden');
                 this.controlsEl.classList.add('hidden'); // Hide controls on success
             } else {
                 this.statusText.innerText = "Failed to stream media Blob!";
             }
             
             // Cleanup execution memfs buffers
             await ffmpegManager.removeFile(file.name);
             await ffmpegManager.removeFile(`out_${this.instanceId}.mp4`);
             
        } else {
             this.statusText.innerText = "Conversion completely failed.";
        }
    }
}

// Bind to Pythra JS injection lifecycle
window.pythraVideoPlayer = {
    initialize: function(elementId, options) {
        return new window.PythraVideoPlayer(elementId, options);
    }
};
