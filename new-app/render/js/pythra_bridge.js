window.PythraBridge = {
    applyPatches: function (patches) {
        if (!Array.isArray(patches)) {
            console.error("PythraBridge: patches must be an array", patches);
            return;
        }

        // ── FLIP Layout Animations: Measure (First) ──
        const layoutElements = document.querySelectorAll('[data-layout="true"], [data-layout-id]');
        const firstBounds = new Map();
        layoutElements.forEach(el => {
            const key = el.getAttribute('data-layout-id') || el.id;
            firstBounds.set(key, el.getBoundingClientRect());
        });

        patches.forEach(patch => {
            try {
                this.processPatch(patch);
            } catch (e) {
                console.error("PythraBridge: Failed to process patch", patch, e);
            }
        });

        // ── FLIP Layout Animations: Invert & Play (Last) ──
        const newLayoutElements = document.querySelectorAll('[data-layout="true"], [data-layout-id]');
        newLayoutElements.forEach(el => {
            const key = el.getAttribute('data-layout-id') || el.id;
            const firstRect = firstBounds.get(key);
            if (firstRect) {
                const lastRect = el.getBoundingClientRect();
                const dx = firstRect.left - lastRect.left;
                const dy = firstRect.top - lastRect.top;
                const dw = lastRect.width > 0 ? firstRect.width / lastRect.width : 1;
                const dh = lastRect.height > 0 ? firstRect.height / lastRect.height : 1;

                if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5 || Math.abs(dw - 1) > 0.005 || Math.abs(dh - 1) > 0.005) {
                    if (window.Motion && window.Motion.animate) {
                        el.style.transformOrigin = '0 0';
                        window.Motion.animate(
                            el,
                            {
                                transform: [
                                    `translate(${dx}px, ${dy}px) scale(${dw}, ${dh})`,
                                    'translate(0px, 0px) scale(1, 1)'
                                ]
                            },
                            {
                                duration: 0.45,
                                ease: [0.25, 1, 0.5, 1]
                            }
                        );
                    }
                }
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
        let tempContainer;
        if (parentEl && (parentEl.namespaceURI === 'http://www.w3.org/2000/svg' || parentEl.tagName.toLowerCase() === 'svg')) {
            tempContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        } else {
            tempContainer = document.createElement('div');
        }
        tempContainer.innerHTML = html.trim();
        const insertedEl = tempContainer.firstElementChild;

        if (!insertedEl) {
            console.warn(`INSERT: No valid element created from HTML for ${targetId}`);
            return;
        }

        // Insert into DOM
        const beforeEl = before_id ? document.getElementById(before_id) : null;

        // Defensive: If inserting a dropdown <li class="dropdown-item"> into a dropdown
        // container, prefer appending it into an existing <ul.dropdown-menu> inside
        // the parent container. This prevents <li> elements from being inserted
        // directly into the wrapper <div> (which was observed in incremental patches).
        if (insertedEl && insertedEl.tagName === 'LI' && insertedEl.classList.contains('dropdown-item')) {
            const menu = parentEl.querySelector('ul.dropdown-menu');
            if (menu) {
                const beforeElInMenu = before_id ? menu.querySelector(`#${before_id}`) : null;
                if (beforeElInMenu && menu.contains(beforeElInMenu)) {
                    menu.insertBefore(insertedEl, beforeElInMenu);
                } else {
                    menu.appendChild(insertedEl);
                }
            } else {
                // No ul found; fall back to inserting into the parent container.
                if (beforeEl && parentEl.contains(beforeEl)) {
                    parentEl.insertBefore(insertedEl, beforeEl);
                } else {
                    parentEl.appendChild(insertedEl);
                }
            }
        } else {
            if (beforeEl && parentEl.contains(beforeEl)) {
                parentEl.insertBefore(insertedEl, beforeEl);
            } else {
                parentEl.appendChild(insertedEl);
            }
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
        if (insertedEl) {
            this.bindReactiveValues(insertedEl);
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

        let tempContainer;
        if (oldEl && oldEl.parentNode && (oldEl.parentNode.namespaceURI === 'http://www.w3.org/2000/svg' || oldEl.parentNode.tagName.toLowerCase() === 'svg')) {
            tempContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        } else {
            tempContainer = document.createElement('div');
        }
        tempContainer.innerHTML = new_html.trim();
        const newEl = tempContainer.firstElementChild;

        if (newEl) {
            oldEl.parentNode.replaceChild(newEl, oldEl);
            if (new_props) {
                this.updateProps(newEl, new_props, null);
            }
            this.bindReactiveValues(newEl);
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
            } else if (key === 'style') {
                // Inject dynamic inline styling for Pythra elements
                if (typeof value === 'object' && value !== null) {
                    for (const [styleKey, styleValue] of Object.entries(value)) {
                        if (typeof styleValue === 'string' && styleValue.startsWith('motion-val:')) {
                            if (el._motionListeners && el._motionListeners.has(styleKey)) {
                                const unsubscribe = el._motionListeners.get(styleKey);
                                if (typeof unsubscribe === 'function') unsubscribe();
                            }
                            const mv = this.resolveMotionValue(styleValue);
                            if (mv) {
                                const unsubscribe = mv.on("change", (latest) => {
                                    el.style.setProperty(styleKey, latest);
                                });
                                el._motionListeners = el._motionListeners || new Map();
                                el._motionListeners.set(styleKey, unsubscribe);
                                el.style.setProperty(styleKey, mv.get());
                            }
                        } else {
                            if (el._motionListeners && el._motionListeners.has(styleKey)) {
                                const unsubscribe = el._motionListeners.get(styleKey);
                                if (typeof unsubscribe === 'function') unsubscribe();
                                el._motionListeners.delete(styleKey);
                            }
                            el.style.setProperty(styleKey, styleValue);
                        }
                    }
                }
            } else if (key === 'attributes') {
                // ── SVG Attributes ────────────────────────────────────────────────────
                if (typeof value === 'object' && value !== null) {
                    for (const [attrName, attrValue] of Object.entries(value)) {
                        if (attrValue === null || attrValue === undefined) {
                            el.removeAttribute(attrName);
                        } else {
                            el.setAttribute(attrName, String(attrValue));
                        }
                    }
                }
            }
            // Add more property handlers as needed from the Python logic
        }
    },

    resolveMotionValue: function (token) {
        if (!token || typeof token !== 'string' || !token.startsWith('motion-val:')) {
            return null;
        }
        if (!window.PythraMotionValues) {
            window.PythraMotionValues = new Map();
        }

        const parts = token.split(':');
        const id = parts[1];

        if (window.PythraMotionValues.has(id)) {
            return window.PythraMotionValues.get(id);
        }

        if (!window.Motion) {
            console.warn("PythraBridge: Motion.dev library not loaded yet.");
            return null;
        }
        console.log("PythraBridge: window.Motion keys:", Object.keys(window.Motion));
        if (typeof window.Motion.motionValue !== 'function') {
            console.warn("PythraBridge: Motion.motionValue is not a function:", typeof window.Motion.motionValue);
            return null;
        }

        if (parts[2] === 'map') {
            const sourceId = parts[3];
            const inputRangeStr = parts[4];
            const outputRangeStr = parts[5];

            let sourceMv = window.PythraMotionValues.get(sourceId);
            if (!sourceMv) {
                sourceMv = window.Motion.motionValue(0.0);
                window.PythraMotionValues.set(sourceId, sourceMv);
            }

            const inputs = inputRangeStr.split(',').map(Number);
            const outputs = outputRangeStr.split(',').map(val => {
                const num = Number(val);
                return isNaN(num) ? val : num;
            });

            if (typeof window.Motion.interpolate === 'function') {
                const interpolator = window.Motion.interpolate(inputs, outputs);
                const mapped = window.Motion.motionValue(interpolator(sourceMv.get()));
                sourceMv.on("change", (latest) => {
                    mapped.set(interpolator(latest));
                });
                window.PythraMotionValues.set(id, mapped);
                return mapped;
            } else if (typeof window.Motion.map === 'function') {
                const mapped = window.Motion.map(sourceMv, inputs, outputs);
                window.PythraMotionValues.set(id, mapped);
                return mapped;
            }
        } else {
            const initialVal = parseFloat(parts[2]) || 0.0;
            const mv = window.Motion.motionValue(initialVal);
            window.PythraMotionValues.set(id, mv);
            return mv;
        }

        return null;
    },

    bindReactiveValues: function (rootEl) {
        console.log("PythraBridge: bindReactiveValues on", rootEl ? (rootEl.id || rootEl.tagName) : null);
        if (!rootEl) return;

        if (!window.Motion || typeof window.Motion.motionValue !== 'function') {
            console.log("PythraBridge: Motion.dev library not loaded yet, scheduling retry in 100ms...");
            setTimeout(() => {
                this.bindReactiveValues(rootEl);
            }, 100);
            return;
        }

        const selector = '[style*="motion-val:"]';
        const elements = rootEl.querySelectorAll ? rootEl.querySelectorAll(selector) : [];
        console.log("PythraBridge: querySelectorAll count:", elements.length);
        
        if (rootEl.getAttribute && rootEl.getAttribute('style') && rootEl.getAttribute('style').includes('motion-val:')) {
            this.processElementReactiveStyles(rootEl);
        }
        elements.forEach(el => {
            this.processElementReactiveStyles(el);
        });
    },

    processElementReactiveStyles: function (el) {
        const rawStyle = el.getAttribute('style');
        console.log("PythraBridge: processElementReactiveStyles rawStyle:", el.id, rawStyle);
        if (!rawStyle || !rawStyle.includes('motion-val:')) return;

        const declarations = rawStyle.split(';');
        declarations.forEach(decl => {
            const index = decl.indexOf(':');
            if (index === -1) return;
            const styleKey = decl.substring(0, index).trim();
            const styleValue = decl.substring(index + 1).trim();

            console.log("PythraBridge: styleKey:", styleKey, "styleValue:", styleValue);

            if (styleValue.startsWith('motion-val:')) {
                if (el._motionListeners && el._motionListeners.has(styleKey)) {
                    const unsubscribe = el._motionListeners.get(styleKey);
                    if (typeof unsubscribe === 'function') unsubscribe();
                }
                const mv = this.resolveMotionValue(styleValue);
                console.log("PythraBridge: resolved mv:", mv);
                if (mv) {
                    const unsubscribe = mv.on("change", (latest) => {
                        console.log("PythraBridge: mv change listener triggered:", styleKey, latest);
                        el.style.setProperty(styleKey, latest);
                    });
                    el._motionListeners = el._motionListeners || new Map();
                    el._motionListeners.set(styleKey, unsubscribe);
                    el.style.setProperty(styleKey, mv.get());
                }
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (window.PythraBridge && window.PythraBridge.bindReactiveValues) {
        window.PythraBridge.bindReactiveValues(document.body);
    }
});
