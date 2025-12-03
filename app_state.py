"""
Application state management for Color Picker.
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ColorState:
    """State for currently selected/hovered color."""
    h: Optional[float] = None
    s: Optional[float] = None
    v: Optional[float] = None
    rgb: Optional[Tuple[int, int, int]] = None
    opp_h: Optional[float] = None
    opp_rgb: Optional[Tuple[int, int, int]] = None


@dataclass
class GradientParams:
    """Parameters for gradient generation."""
    steps: int = 20
    curve: float = 0.0
    fine_shade1: float = 1.0
    fine_shade2: float = 1.0
    fine_hue2: float = 0.0
    
    def get_all_params(self, h1, s1, v1, h2, s2, v2, shade):
        """Get all parameters as tuple for gradient functions."""
        return (
            self.steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.curve, shade
        )


@dataclass
class AppState:
    """Complete application state."""
    hue_shift: float = 0.0
    shade: float = 1.0
    locked: bool = False
    last_panel: str = "wheel"
    last_square_idx: Optional[int] = None
    hovered_square_idx: Optional[int] = None
    
    color: ColorState = None
    gradient: GradientParams = None
    
    def __post_init__(self):
        if self.color is None:
            self.color = ColorState()
        if self.gradient is None:
            self.gradient = GradientParams()
