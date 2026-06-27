from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union


@dataclass
class AnimationOptions:
    type: str = "tween"
    duration: float = 0.3
    delay: float = 0.0
    ease: Any = "easeOut"
    repeat: int = 0
    repeat_type: str = "loop"
    repeat_delay: float = 0.0
    direction: Optional[str] = None
    end_delay: Optional[float] = None
    bounce: Optional[float] = None
    stiffness: Optional[float] = None
    damping: Optional[float] = None
    mass: Optional[float] = None
    velocity: Optional[float] = None
    visual_duration: Optional[float] = None

    # ── Path Options ──────────────────────────────────────────────────────
    path: Optional[str] = None
    path_strength: Optional[float] = None
    path_peak: Optional[float] = None
    path_direction: Optional[str] = None
    path_rotate: Optional[bool] = None

    # ── Target Selector ───────────────────────────────────────────────────
    selector: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "type": self.type,
            "duration": self.duration,
            "delay": self.delay,
            "ease": self.ease,
        }
        if self.repeat:
            d["repeat"] = self.repeat
            d["repeatType"] = self.repeat_type
        if self.repeat_delay:
            d["repeatDelay"] = self.repeat_delay
        if self.direction is not None:
            d["direction"] = self.direction
        if self.end_delay is not None:
            d["endDelay"] = self.end_delay
        if self.bounce is not None:
            d["bounce"] = self.bounce
        if self.stiffness is not None:
            d["stiffness"] = self.stiffness
        if self.damping is not None:
            d["damping"] = self.damping
        if self.mass is not None:
            d["mass"] = self.mass
        if self.velocity is not None:
            d["velocity"] = self.velocity
        if self.visual_duration is not None:
            d["visualDuration"] = self.visual_duration
        if self.path is not None:
            d["path"] = self.path
        if self.path_strength is not None:
            d["pathStrength"] = self.path_strength
        if self.path_peak is not None:
            d["pathPeak"] = self.path_peak
        if self.path_direction is not None:
            d["pathDirection"] = self.path_direction
        if self.path_rotate is not None:
            d["pathRotate"] = self.path_rotate
        if self.selector is not None:
            d["selector"] = self.selector
        return d


@dataclass
class ScrollOptions:
    target_selector: Optional[str] = None
    axis: str = "y"
    offset: List[str] = field(default_factory=lambda: ["start end", "end start"])
    container_selector: Optional[str] = None
    margin: str = "0px"
    amount: Union[float, str] = 0.1


@dataclass
class InViewOptions:
    once: bool = True
    margin: str = "0px"
    amount: Union[float, str] = 0.1
    container_selector: Optional[str] = None


@dataclass
class TimelineStep:
    target: Optional[str] = None
    keyframes: Optional[dict] = None
    options: Optional[dict] = None
    at: Optional[float] = None


KeyframeValue = Union[float, int, str, List[Union[float, int, str]]]
Keyframes = Dict[str, KeyframeValue]
