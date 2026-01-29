window.PythraBridge = {
    applyPatches: function (patches) {
        if (!Array.isArray(patches)) {
            console.error("PythraBridge: patches must be an array", patches);
            return;
        }

        patches.forEach(patch => {
            try {
                this.processPatch(patch);
            } catch (e) {
                console.error("PythraBridge: Failed to process patch", patch, e);
            }
        });
    },

    processPatch: function (patch) {
        const { action, html_id, data } = patch;

        switch (action) {
            case "INSERT":
                this.handleInsert(html_id, data);
                break;
            case "REMOVE":
                this.handleRemove(html_id);
                break;
            case "UPDATE":
                this.handleUpdate(html_id, data);
                break;
            case "MOVE":
                this.handleMove(html_id, data);
                break;
            case "REPLACE":
                this.handleReplace(html_id, data);
                break;
            default:
                console.warn("PythraBridge: Unknown action", action);
        }
    },

    handleInsert: function (targetId, data) {
        const { parent_html_id, html, props, before_id } = data;
        const parentEl = document.getElementById(parent_html_id);

        if (!parentEl) {
            console.error(`INSERT: Parent element ${parent_html_id} not found for ${targetId}`);
            return;
        }

        // Create a temporary container to parse HTML
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = html.trim();
        const insertedEl = tempContainer.firstElementChild;

        if (!insertedEl) {
            console.warn(`INSERT: No valid element created from HTML for ${targetId}`);
            return;
        }

        // Insert into DOM
        const beforeEl = before_id ? document.getElementById(before_id) : null;
        if (beforeEl && parentEl.contains(beforeEl)) {
            parentEl.insertBefore(insertedEl, beforeEl);
        } else {
            parentEl.appendChild(insertedEl);
        }

        // Apply properties specifically (logic that might not be in the HTML stub)
        if (props) {
            this.updateProps(insertedEl, props, null);
        }

        // Handle special Initializers that were embedded in the patch logic before
        if (props && props.init_gradient_clip_border && typeof PythraGradientClipPath !== 'undefined') {
            setTimeout(() => {
                window._pythra_instances = window._pythra_instances || {};
                window._pythra_instances[targetId] = new PythraGradientClipPath(targetId, props.gradient_clip_options || {});
            }, 0);
        }
    },

    handleRemove: function (targetId) {
        const el = document.getElementById(targetId);
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);

            // Cleanup instances
            if (window._pythra_instances && window._pythra_instances[targetId]) {
                delete window._pythra_instances[targetId];
            }
        }
    },

    handleUpdate: function (targetId, data) {
        const el = document.getElementById(targetId);
        if (!el) {
            console.error(`UPDATE: Element ${targetId} not found`);
            return;
        }

        const { props, old_props } = data;
        this.updateProps(el, props, old_props);
    },

    handleMove: function (targetId, data) {
        const { parent_html_id, before_id } = data;
        const el = document.getElementById(targetId);
        const parentEl = document.getElementById(parent_html_id);

        if (!el || !parentEl) return;

        const beforeEl = before_id ? document.getElementById(before_id) : null;
        if (beforeEl && parentEl.contains(beforeEl)) {
            parentEl.insertBefore(el, beforeEl);
        } else {
            parentEl.appendChild(el);
        }
    },

    handleReplace: function (targetId, data) {
        const { new_html, new_props } = data;
        const oldEl = document.getElementById(targetId);
        if (!oldEl || !oldEl.parentNode) return;

        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = new_html.trim();
        const newEl = tempContainer.firstElementChild;

        if (newEl) {
            oldEl.parentNode.replaceChild(newEl, oldEl);
            if (new_props) {
                this.updateProps(newEl, new_props, null);
            }
        }
    },

    updateProps: function (el, props, oldProps) {
        if (!props) return;

        for (const [key, value] of Object.entries(props)) {
            if (key === 'css_class') {
                const oldClass = props.old_shared_class || (oldProps ? oldProps.css_class : null);
                const newClass = value;

                if (oldClass !== newClass) {
                    if (oldClass) {
                        oldClass.split(' ').forEach(c => c && el.classList.remove(c));
                    }
                    if (newClass) {
                        newClass.split(' ').forEach(c => c && el.classList.add(c));
                    }
                }
            } else if (key === 'data') {
                el.textContent = String(value);
            } else if (key === 'src') {
                el.src = value;
            } else if (key === 'tooltip') {
                el.title = value;
            } else if (key === 'value') {
                // Handle input values carefully to avoid cursor jumps
                if (el.value !== String(value)) {
                    el.value = String(value);
                }
            } else if (key === 'errorText') {
                // Handle error text helper (special logic from python)
                const helperId = el.id + "_helper";
                const helperEl = document.getElementById(helperId);
                if (helperEl) helperEl.textContent = String(value);
            }
            // Add more property handlers as needed from the Python logic
        }
    }
};
