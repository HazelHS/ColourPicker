"""
Gradient and color palette generation logic.
"""
from color_utils import hsv_to_rgb255, rgb_to_hex, get_colour_name


class GradientCalculator:
    """Calculate color gradients and palettes."""
    
    def __init__(self):
        """Initialize gradient calculator."""
        self.shade_adjust = 0.0
        self.hue_adjust = 0.0
        self.sat_adjust = 0.0
        self.hue_spread = 1.0
    
    def set_adjustments(self, shade_adjust, hue_adjust, sat_adjust, hue_spread):
        """
        Set adjustment parameters for gradient generation.
        
        Args:
            shade_adjust: Brightness adjustment (-1 to 1)
            hue_adjust: Hue rotation adjustment (-1 to 1)
            sat_adjust: Saturation adjustment (-1 to 1)
            hue_spread: Hue spreading factor (0 to 2)
        """
        self.shade_adjust = shade_adjust
        self.hue_adjust = hue_adjust
        self.sat_adjust = sat_adjust
        self.hue_spread = hue_spread
    
    def generate_gradient(self, base_h, base_s, base_v, num_colors=11):
        """
        Generate a gradient of colors based on a base color and adjustments.
        
        Args:
            base_h: Base hue (0-1)
            base_s: Base saturation (0-1)
            base_v: Base value/brightness (0-1)
            num_colors: Number of colors to generate
        
        Returns:
            List of (rgb, hex, name) tuples
        """
        gradient = []
        
        for i in range(num_colors):
            # Calculate fraction from -1 to +1 for symmetric gradient
            frac = -1 + 2 * i / (num_colors - 1) if num_colors > 1 else 0
            
            # Apply adjustments
            h_new = (base_h + frac * self.hue_spread * 0.1 + self.hue_adjust) % 1.0
            s_new = max(0.0, min(1.0, base_s + frac * self.sat_adjust * 0.3))
            v_new = max(0.0, min(1.0, base_v + frac * self.shade_adjust * 0.3))
            
            rgb = hsv_to_rgb255(h_new, s_new, v_new)
            hex_code = rgb_to_hex(rgb)
            name = get_colour_name(rgb)
            
            gradient.append((rgb, hex_code, name))
        
        return gradient
    
    def adjust_color(self, h, s, v):
        """
        Apply current adjustments to a single color.
        
        Args:
            h: Hue (0-1)
            s: Saturation (0-1)
            v: Value/brightness (0-1)
        
        Returns:
            Tuple of (h, s, v) with adjustments applied
        """
        h_new = (h + self.hue_adjust) % 1.0
        s_new = max(0.0, min(1.0, s + self.sat_adjust * 0.3))
        v_new = max(0.0, min(1.0, v + self.shade_adjust * 0.3))
        
        return h_new, s_new, v_new


def curve_t(t, curve):
    """
    Apply curve transformation to interpolation value.
    """
    c = curve / 100.0
    if c == 0:
        return t
    elif c > 0:
        return t ** (1 / (1 + c * 2))
    else:
        return t ** (1 - c * 2)


def calculate_gradient_colors(
    steps, h1, s1, v1, h2, s2, v2, fine_shade1, fine_shade2, fine_hue2, gradient_curve, shade
):
    """
    Calculate a list of RGB colors for the gradient.
    Returns a list of (r, g, b) tuples.
    """
    from color_utils import hsv_to_rgb255
    v1 = shade * fine_shade1
    v2 = shade * fine_shade2
    h2 = (h2 + fine_hue2) % 1.0
    colors = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        t_curve = curve_t(t, gradient_curve)
        dh = ((h2 - h1 + 1.5) % 1.0) - 0.5
        h = (h1 + t_curve * dh) % 1.0
        s = s1 + t_curve * (s2 - s1)
        v = v1 + t_curve * (v2 - v1)
        rgb = hsv_to_rgb255(h, s, v)
        colors.append(rgb)
    return colors
