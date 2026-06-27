(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['motion'], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory(require('motion'));
    } else if (root.Motion && root.Motion.animate) {
        root.PythraMotion = factory(root.Motion);
    } else {
        root._pythraMotionQueue = root._pythraMotionQueue || [];
        var script = document.createElement('script');
        script.src = root.PYTHRA_MOTION_JS_PATH || '/packages/pythra_motion/js/motion.js';
        script.onload = function () {
            var MotionLib = root.Motion || {};
            root.PythraMotion = factory(MotionLib);
            var queue = root._pythraMotionQueue;
            delete root._pythraMotionQueue;
            queue.forEach(function (fn) { try { fn(); } catch (e) {} });
        };
        script.onerror = function () {
            console.error('PythraMotion: failed to load motion.js');
            root.PythraMotion = factory({});
        };
        if (document.head) {
            document.head.appendChild(script);
        } else {
            document.addEventListener('DOMContentLoaded', function () {
                document.head.appendChild(script);
            });
        }
    }
}(typeof self !== 'undefined' ? self : this, function (Motion) {

    var MotionAPI = Motion.animate ? Motion : (window.Motion || {});

    if (!PythraMotion._entrancePlayed) PythraMotion._entrancePlayed = {};

    function PythraMotion(elementOrId, options) {
        this.element = typeof elementOrId === 'string'
            ? document.getElementById(elementOrId)
            : elementOrId;

        if (!this.element) {
            console.error('PythraMotion: element not found');
            return;
        }

        this.options = options || {};
        this.animations = {};
        this.animationIdCounter = 0;
        this.callback = this.options.callback || null;
        this.instanceId = this.options.instanceId || '';

        this._initialized = true;

        var self = this;
        var alreadyInited = PythraMotion._entrancePlayed[this.instanceId];
        PythraMotion._entrancePlayed[this.instanceId] = true;

        if (!alreadyInited) {
            if (this.options.entranceAnimation) {
                setTimeout(function () {
                    if (!self.element || !self.element.isConnected) return;
                    self.animate(self.options.entranceAnimation, self.options.entranceOptions || {});
                }, 50);
            }

            if (this.options.scrollOptions && this.options.scrollAnimation) {
                setTimeout(function () {
                    if (!self.element || !self.element.isConnected) return;
                    self.scrollAnimate(self.options.scrollAnimation, self.options.scrollOptions);
                }, 50);
            }

            if (this.options.inViewOptions && this.options.inViewAnimation) {
                setTimeout(function () {
                    if (!self.element || !self.element.isConnected) return;
                    self.inViewAnimate(self.options.inViewAnimation, self.options.inViewOptions);
                }, 50);
            }

            if (this.options.hoverAnimationEnter || this.options.hoverAnimationLeave) {
                setTimeout(function () {
                    if (!self.element || !self.element.isConnected) return;
                    self.hoverAnimate(
                        self.options.hoverAnimationEnter || null,
                        self.options.hoverAnimationLeave || null,
                        self.options.hoverOptions || {}
                    );
                }, 50);
            }

            if (this.options.pressAnimationStart || this.options.pressAnimationEnd) {
                setTimeout(function () {
                    if (!self.element || !self.element.isConnected) return;
                    self.pressAnimate(
                        self.options.pressAnimationStart || null,
                        self.options.pressAnimationEnd || null,
                        self.options.pressOptions || {}
                    );
                }, 50);
            }
        }
    }

    function generateId(prefix) {
        return (prefix || 'anim_') + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
    }

    function _findScrollContainer(el) {
        var parent = el.parentElement;
        while (parent) {
            var style = window.getComputedStyle(parent);
            if (style.overflowY === 'auto' || style.overflowY === 'scroll' ||
                style.overflow === 'auto' || style.overflow === 'scroll') {
                return parent;
            }
            parent = parent.parentElement;
        }
        return document.scrollingElement;
    }

    function _resolveTarget(el, options) {
        if (options && options.selector) {
            var targets = el.querySelectorAll(options.selector);
            if (targets.length === 1) return targets[0];
            if (targets.length > 1) return targets;
        }
        return el;
    }

    function _resolveSelectorTarget(rootEl, target) {
        if (typeof target === 'string' && rootEl) {
            try {
                var targets = rootEl.querySelectorAll(target);
                console.log("PythraMotion selector:", target, "found count:", targets.length);
                if (targets.length > 0) {
                    console.log("PythraMotion target[0] tagName:", targets[0].tagName, "namespace:", targets[0].namespaceURI);
                }
                if (targets.length === 1) return targets[0];
                if (targets.length > 1) return Array.from(targets);
            } catch (e) {
                console.error("Error resolving selector target:", target, e);
            }
        }
        return target;
    }

    function _nudgeKeyframes(keyframes) {
        if (!keyframes) return keyframes;
        if (Array.isArray(keyframes)) {
            if (keyframes.length === 2 && keyframes[0] === keyframes[1]) {
                if (typeof keyframes[0] === 'number') {
                    keyframes[1] = keyframes[0] === 0 ? 0.0001 : keyframes[0] + 0.0001;
                }
            }
        } else if (typeof keyframes === 'object') {
            for (var prop in keyframes) {
                if (Object.prototype.hasOwnProperty.call(keyframes, prop)) {
                    var val = keyframes[prop];
                    if (Array.isArray(val) && val.length === 2 && val[0] === val[1]) {
                        if (typeof val[0] === 'number') {
                            val[1] = val[0] === 0 ? 0.0001 : val[0] + 0.0001;
                        }
                    }
                }
            }
        }
        return keyframes;
    }

    // ── Path Options & Easing Resolution ──────────────────────────────────
    function _resolveMotionOptions(animOptions) {
        var motionOptions = {};
        if (!animOptions) return motionOptions;

        if (animOptions.type) motionOptions.type = animOptions.type;
        if (animOptions.duration !== undefined) motionOptions.duration = animOptions.duration;
        if (animOptions.delay !== undefined) motionOptions.delay = animOptions.delay;
        if (animOptions.ease !== undefined) motionOptions.ease = animOptions.ease;
        if (animOptions.repeat !== undefined) motionOptions.repeat = animOptions.repeat;
        if (animOptions.repeatType !== undefined) motionOptions.repeatType = animOptions.repeatType;
        if (animOptions.repeatDelay !== undefined) motionOptions.repeatDelay = animOptions.repeatDelay;
        if (animOptions.direction !== undefined) motionOptions.direction = animOptions.direction;
        if (animOptions.endDelay !== undefined) motionOptions.endDelay = animOptions.endDelay;
        if (animOptions.bounce !== undefined) motionOptions.bounce = animOptions.bounce;
        if (animOptions.stiffness !== undefined) motionOptions.stiffness = animOptions.stiffness;
        if (animOptions.damping !== undefined) motionOptions.damping = animOptions.damping;
        if (animOptions.mass !== undefined) motionOptions.mass = animOptions.mass;
        if (animOptions.velocity !== undefined) motionOptions.velocity = animOptions.velocity;
        if (animOptions.visualDuration !== undefined) motionOptions.visualDuration = animOptions.visualDuration;

        if (animOptions.path === 'arc' && MotionAPI.arc) {
            var arcConfig = {};
            if (animOptions.pathStrength !== undefined) arcConfig.strength = animOptions.pathStrength;
            if (animOptions.pathPeak !== undefined) arcConfig.peak = animOptions.pathPeak;
            if (animOptions.pathDirection !== undefined) arcConfig.direction = animOptions.pathDirection;
            if (animOptions.pathRotate !== undefined) arcConfig.rotate = animOptions.pathRotate;
            motionOptions.path = MotionAPI.arc(arcConfig);
        }

        return motionOptions;
    }

    PythraMotion.prototype._notify = function (eventType, data) {
        if (this.callback && typeof window.handleInput === 'function') {
            window.handleInput(this.callback, JSON.stringify({
                type: eventType,
                instanceId: this.instanceId,
                data: data
            }));
        }
    };

    PythraMotion.prototype.animate = function (keyframes, options) {
        var self = this;
        var animOptions = options || {};
        var id = animOptions.id || generateId('anim_');

        keyframes = _nudgeKeyframes(keyframes);
        var motionOptions = _resolveMotionOptions(animOptions);

        if (animOptions.onUpdate) {
            motionOptions.onUpdate = function (v) {
                self._notify('update', { animationId: id, value: v });
            };
        }
        if (animOptions.onPlay) {
            motionOptions.onPlay = function () {
                self._notify('play', { animationId: id });
            };
        }
        if (animOptions.onStop) {
            motionOptions.onStop = function () {
                self._notify('stop', { animationId: id });
            };
        }

        motionOptions.onComplete = function () {
            self._notify('complete', { animationId: id });
        };

        var target = _resolveTarget(self.element, animOptions);
        if (MotionAPI.animate) {
            var controls = MotionAPI.animate(target, keyframes, motionOptions);
            self.animations[id] = controls;
        } else {
            console.error('PythraMotion: motion.js not loaded');
        }

        return id;
    };

    PythraMotion.prototype.scrollAnimate = function (keyframes, scrollOptions) {
        var self = this;
        var sopts = scrollOptions || {};
        var animOpts = sopts.animationOptions || {};

        var motionOptions = _resolveMotionOptions(animOpts);
        if (!motionOptions.ease) motionOptions.ease = 'linear';
        if (motionOptions.duration === undefined) motionOptions.duration = 1;

        if (MotionAPI.animate && MotionAPI.scroll) {
            var target = _resolveTarget(self.element, animOpts);
            var animation = MotionAPI.animate(target, keyframes, motionOptions);

            var targetEl = sopts.targetSelector
                ? document.querySelector(sopts.targetSelector)
                : target;

            var containerEl = sopts.containerSelector
                ? document.querySelector(sopts.containerSelector)
                : _findScrollContainer(self.element);

            MotionAPI.scroll(animation, {
                target: targetEl,
                container: containerEl,
                offset: sopts.offset || ['start end', 'end start'],
                axis: sopts.axis || 'y',
            });

            var id = generateId('scroll_');
            self.animations[id] = animation;
            return id;
        }
        return null;
    };

    PythraMotion.prototype.inViewAnimate = function (keyframes, viewOptions) {
        var self = this;
        var vopts = viewOptions || {};
        var animOpts = vopts.animationOptions || {};

        if (MotionAPI.inView && MotionAPI.animate) {
            var observerOpts = {
                margin: vopts.margin || '0px',
                amount: vopts.amount !== undefined ? vopts.amount : 0.1,
            };
            var rootEl = vopts.containerSelector
                ? document.querySelector(vopts.containerSelector)
                : _findScrollContainer(self.element);
            if (rootEl !== document.scrollingElement) {
                observerOpts.root = rootEl;
            }

            var stopFn = MotionAPI.inView(self.element, function () {
                var motionOptions = _resolveMotionOptions(animOpts);
                var target = _resolveTarget(self.element, animOpts);
                var controls = MotionAPI.animate(target, keyframes, motionOptions);
                var id = generateId('inview_');
                self.animations[id] = controls;
                self._notify('inView', { animationId: id });
                if (!vopts.repeat) {
                    stopFn();
                }
                return stopFn;
            }, observerOpts);

            return stopFn;
        }
        return null;
    };

    PythraMotion.prototype.hoverAnimate = function (keyframesEnter, keyframesLeave, options) {
        var self = this;
        var opts = options || {};
        var target = _resolveTarget(self.element, opts);

        if (MotionAPI.hover) {
            return MotionAPI.hover(
                self.element,
                function () {
                    if (keyframesEnter) {
                        var motionOptions = _resolveMotionOptions(opts);
                        var ctrl = MotionAPI.animate(target, keyframesEnter, motionOptions);
                        var id = generateId('hover_');
                        self.animations[id] = ctrl;
                    }
                },
                function () {
                    if (keyframesLeave) {
                        var motionOptions = _resolveMotionOptions(opts);
                        var ctrl = MotionAPI.animate(target, keyframesLeave, motionOptions);
                        var id = generateId('hover_leave_');
                        self.animations[id] = ctrl;
                    }
                }
            );
        }
        return null;
    };

    PythraMotion.prototype.pressAnimate = function (keyframesStart, keyframesEnd, options) {
        var self = this;
        var opts = options || {};
        var target = _resolveTarget(self.element, opts);

        if (MotionAPI.press) {
            return MotionAPI.press(
                self.element,
                function () {
                    if (keyframesStart) {
                        var motionOptions = _resolveMotionOptions(opts);
                        var ctrl = MotionAPI.animate(target, keyframesStart, motionOptions);
                        self.animations[generateId('press_')] = ctrl;
                    }
                },
                function () {
                    if (keyframesEnd) {
                        var motionOptions = _resolveMotionOptions(opts);
                        var ctrl = MotionAPI.animate(target, keyframesEnd, motionOptions);
                        self.animations[generateId('press_end_')] = ctrl;
                    }
                }
            );
        }
        return null;
    };

    PythraMotion.prototype.staggerChildren = function (selector, keyframes, options) {
        var self = this;
        var opts = options || {};
        var children = self.element.querySelectorAll(selector);

        if (children.length === 0) return;

        var motionOptions = _resolveMotionOptions(opts);

        if (MotionAPI.animate && MotionAPI.stagger) {
            motionOptions.delay = MotionAPI.stagger(opts.staggerDelay || 0.05, {
                from: opts.staggerFrom || 'first',
                startDelay: opts.startDelay || 0,
            });
            var controls = MotionAPI.animate(children, keyframes, motionOptions);
            var id = generateId('stagger_');
            self.animations[id] = controls;
            return id;
        }
        return null;
    };

    PythraMotion.prototype.timeline = function (sequence, options) {
        console.log("PythraMotion: timeline called with:", JSON.stringify(sequence));
        var self = this;
        if (MotionAPI.timeline) {
            var resolvedOptions = _resolveMotionOptions(options);
            var resolvedSequence = sequence.map(function (step) {
                if (Array.isArray(step) && step.length >= 2) {
                    var newStep = step.slice();
                    var resolvedTarget = _resolveSelectorTarget(self.element, step[0]);
                    console.log("PythraMotion: target", step[0], "resolved to:", resolvedTarget);
                    newStep[0] = resolvedTarget;
                    if (step.length >= 3) {
                        var stepOptions = step[2];
                        if (stepOptions && typeof stepOptions === 'object') {
                            newStep[2] = _resolveMotionOptions(stepOptions);
                        }
                    }
                    return newStep;
                }
                return step;
            });

            try {
                console.log("PythraMotion: calling MotionAPI.timeline with resolvedSequence:", resolvedSequence);
                var controls = MotionAPI.timeline(resolvedSequence, resolvedOptions);
                console.log("PythraMotion: timeline controls generated:", controls);
                var id = generateId('timeline_');
                this.animations[id] = controls;
                return id;
            } catch (err) {
                console.error("PythraMotion: Error during MotionAPI.timeline:", err);
            }
        }

        // Custom Timeline Polyfill using individual animate calls
        console.log("PythraMotion: MotionAPI.timeline not available, using custom polyfill.");
        var prevStepEnd = 0;
        var animationControls = [];
        self.timers = self.timers || [];

        sequence.forEach(function (step) {
            if (!Array.isArray(step) || step.length < 2) return;
            var target = _resolveSelectorTarget(self.element, step[0]);
            if (!target) return;

            var keyframes = _nudgeKeyframes(step[1]);
            var stepOptions = step[2] || {};
            var resolvedOpts = _resolveMotionOptions(stepOptions);

            var delay = 0;
            var duration = resolvedOpts.duration !== undefined ? resolvedOpts.duration : 0.3;

            if (stepOptions.at !== undefined) {
                var at = stepOptions.at;
                if (typeof at === 'number') {
                    delay = at;
                } else if (typeof at === 'string') {
                    if (at.startsWith('+=')) {
                        delay = prevStepEnd + parseFloat(at.slice(2));
                    } else if (at.startsWith('-=')) {
                        delay = prevStepEnd - parseFloat(at.slice(2));
                    } else {
                        delay = parseFloat(at) || 0;
                    }
                }
            } else {
                delay = prevStepEnd;
            }

            var runDelayMs = delay * 1000;
            resolvedOpts.delay = 0; // Handled by setTimeout

            console.log("PythraMotion timeline polyfill: scheduling", step[0], "to run in", runDelayMs, "ms with duration:", duration);

            var timerId = setTimeout(function () {
                var controls = MotionAPI.animate(target, keyframes, resolvedOpts);
                if (controls) {
                    animationControls.push(controls);
                }
            }, runDelayMs);
            self.timers.push(timerId);

            var stepEnd = delay + duration;
            prevStepEnd = stepEnd;
        });

        // Diagnostic polling to inspect styles in DOM
        var debugCount = 0;
        var debugTimer = setInterval(function() {
            debugCount++;
            var droplet = self.element.querySelector(".splash-droplet");
            if (droplet) {
                var computedOpacity = window.getComputedStyle(droplet).opacity;
                console.log("PythraMotion Debug [" + debugCount + "] - droplet style attribute:", droplet.getAttribute("style"), "transform:", droplet.style.transform, "inline opacity:", droplet.style.opacity, "computed opacity:", computedOpacity);
            } else {
                console.log("PythraMotion Debug [" + debugCount + "] - droplet element not found in DOM");
            }
        }, 100);
        setTimeout(function() { clearInterval(debugTimer); }, 2000);

        var id = generateId('timeline_polyfill_');
        var mockControls = {
            play: function () { animationControls.forEach(function (c) { if (c.play) c.play(); }); },
            pause: function () { animationControls.forEach(function (c) { if (c.pause) c.pause(); }); },
            stop: function () {
                animationControls.forEach(function (c) { if (c.stop) c.stop(); });
                if (self.timers) {
                    self.timers.forEach(clearTimeout);
                    self.timers = [];
                }
            },
            cancel: function () {
                animationControls.forEach(function (c) { if (c.cancel) c.cancel(); });
                if (self.timers) {
                    self.timers.forEach(clearTimeout);
                    self.timers = [];
                }
            },
            reverse: function () { animationControls.forEach(function (c) { if (c.reverse) c.reverse(); }); },
            setSpeed: function (s) { animationControls.forEach(function (c) { if (c.setSpeed) c.setSpeed(s); }); },
            setTime: function (t) { animationControls.forEach(function (c) { if (c.setTime) c.setTime(t); }); },
        };
        this.animations[id] = mockControls;
        return id;
    };

    PythraMotion.prototype.getKeyframes = function () {
        if (MotionAPI.keyframes) {
            return MotionAPI.keyframes.apply(MotionAPI, arguments);
        }
        return null;
    };

    PythraMotion.prototype.getSpring = function (config) {
        if (MotionAPI.spring) {
            return MotionAPI.spring(config || {});
        }
        return null;
    };

    PythraMotion.prototype.getEasing = function (name) {
        if (MotionAPI.easing && MotionAPI.easing[name]) {
            return MotionAPI.easing[name];
        }
        return null;
    };

    PythraMotion.prototype.control = function (animationId, command, value) {
        var anim = this.animations[animationId];
        if (!anim) {
            console.warn('PythraMotion: animation not found:', animationId);
            return;
        }

        switch (command) {
            case 'play':
                anim.play();
                break;
            case 'pause':
                anim.pause();
                break;
            case 'stop':
                anim.stop();
                delete this.animations[animationId];
                break;
            case 'reverse':
                anim.speed = -1;
                anim.play();
                break;
            case 'setSpeed':
                anim.speed = value;
                break;
            case 'setTime':
                anim.time = value;
                break;
            case 'complete':
                anim.complete();
                break;
        }
    };

    PythraMotion.prototype.destroyAll = function () {
        for (var key in this.animations) {
            if (this.animations.hasOwnProperty(key)) {
                try { this.animations[key].stop(); } catch (e) {}
            }
        }
        this.animations = {};
    };

    PythraMotion.prototype.destroy = function () {
        this.destroyAll();
        this._initialized = false;
    };

    // ── Spring Solver Bridge ──────────────────────────────────────────────

    PythraMotion.solveSpring = function (config, timeMs) {
        if (!MotionAPI.spring) return null;
        var solver = MotionAPI.spring(config);
        if (Array.isArray(timeMs)) {
            return timeMs.map(function (t) {
                return solver.next(t).value;
            });
        }
        return solver.next(timeMs).value;
    };

    PythraMotion.solveSpringDetails = function (config, timesMs) {
        if (!MotionAPI.spring) return null;
        var solver = MotionAPI.spring(config);
        var points = (timesMs || []).map(function (t) {
            return solver.next(t).value;
        });
        var duration = solver.calculatedDuration;
        if (duration === null || duration === undefined) {
            // Step solver to find when it reaches rest (done === true)
            var t = 0;
            var step = 10;
            var maxT = 10000; // Cap at 10 seconds to prevent hang
            while (t < maxT) {
                var sample = solver.next(t);
                if (sample.done) {
                    break;
                }
                t += step;
            }
            duration = t;
        }
        return {
            points: points,
            duration: duration
        };
    };

    return PythraMotion;
}));
