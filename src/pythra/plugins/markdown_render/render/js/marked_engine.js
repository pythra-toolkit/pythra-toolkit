window.PythraMarkdownRender = class PythraMarkdownRender {
    constructor(elementOrId, options) {
        this.elementOrId = elementOrId;
        this.options = options;
        this.instanceId = options.instanceId;
        
        // Wait for the container element to exist in the DOM
        setTimeout(() => this.init(), 0);
    }
    
    init() {
        // Pythra passes the actual DOM element or an ID string
        this.container = typeof this.elementOrId === 'string' 
            ? document.getElementById(this.elementOrId) 
            : this.elementOrId;
            
        if (!this.container) {
            console.error("PythraMarkdownRender: Container not found for ", this.elementOrId);
            return;
        }
        
        // Register this instance in Pythra's global tracking so Python can find it
        if (!window._pythra_instances) {
            window._pythra_instances = {};
        }
        window._pythra_instances[this.instanceId] = this;
        
        // Safely resolve dependencies whether they attached to window (globalThis) or local closure wrapper
        this.marked = window.marked || (typeof marked !== 'undefined' ? marked : null);
        this.DOMPurify = window.DOMPurify || (typeof DOMPurify !== 'undefined' ? DOMPurify : null);
        this.hljs = window.hljs || (typeof hljs !== 'undefined' ? hljs : null);

        // Ensure Vendor JS libraries are loaded
        if (!this.marked || !this.DOMPurify || !this.hljs) {
            console.error(`PythraMarkdownRender: Missing dependencies! marked: ${!!this.marked}, DOMPurify: ${!!this.DOMPurify}, hljs: ${!!this.hljs}`);
            return;
        }

        // Configure Marked
        this.marked.setOptions({
            breaks: true,
            gfm: true
        });
        
        // Create the inner content wrapper
        this.innerContainer = document.createElement('div');
        this.innerContainer.className = 'markdown-render-inner-container';
        
        // Apply Initial Styles from Python
        if (this.options.style) {
            Object.assign(this.innerContainer.style, this.options.style);
        }
        
        this.container.appendChild(this.innerContainer);
        
        // Render any initial markdown text provided
        if (this.options.initialMarkdown) {
            this.renderMarkdown(this.options.initialMarkdown);
        }
    }
    
    // Exposed function called by Python framework to update markdown dynamically
    renderMarkdown(markdownText) {
        if (!this.innerContainer || !this.marked || !this.DOMPurify) {
            console.error("Markdown dependencies missing or container not ready");
            return;
        }
        
        // 1. Parse markdown to HTML using marked.js
        const rawHtml = this.marked.parse(markdownText);
        
        // 2. Sanitize HTML using DOMPurify for security (prevents XSS)
        const cleanHtml = this.DOMPurify.sanitize(rawHtml);
        
        // 3. Inject safe HTML
        this.innerContainer.innerHTML = cleanHtml;
        
        // 4. Apply syntax highlighting to code blocks
        if (this.hljs) {
            this.innerContainer.querySelectorAll('pre code').forEach((block) => {
                this.hljs.highlightElement(block);
            });
        }
    }
}

// Attach the initializer for Pythra to invoke
window.pythraMarkdownRender = {
    initialize: function(elementId, options) {
        return new PythraMarkdownRender(elementId, options);
    }
};
