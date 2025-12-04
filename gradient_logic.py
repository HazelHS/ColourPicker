"""
Gradient and color palette generation logic.
"""
from color_utils import hsv_to_rgb255_quantized, get_color_info


def curve_t(t, curve):
    """
    Apply curve transformation to interpolation value.
    
    Args:
        t: Interpolation value (0-1)
        curve: Curve adjustment (-100 to 100)
    
    Returns:
        Transformed t value
    """
    c = curve / 100.0
    if c == 0:
        return t
    elif c > 0:
        return t ** (1 / (1 + c * 2))
    else:
        return t ** (1 - c * 2)


def calculate_gradient_colors(
    steps, h1, s1, v1, h2, s2, v2, fine_shade1, fine_shade2, fine_hue2, gradient_curve, shade, levels=65536
):
    """
    Calculate a list of RGB colors for the gradient.
    
    Args:
        steps: Number of colors in gradient
        h1, s1, v1: Start color HSV
        h2, s2, v2: End color HSV
        fine_shade1, fine_shade2: Fine-tune shade adjustments
        fine_hue2: Fine-tune hue adjustment for end color
        gradient_curve: Curve adjustment value
        shade: Overall shade value
        levels: Number of color levels
    
    Returns:
        List of (r, g, b) tuples
    """
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
        rgb = hsv_to_rgb255_quantized(h, s, v, levels)
        colors.append(rgb)
    
    return colors


def get_gradient_color_at_index(
    idx, steps, h1, s1, v1, h2, s2, v2,
    fine_shade1, fine_shade2, fine_hue2, gradient_curve, shade, levels=65536
):
    """
    Calculate color information for a specific gradient index.
    
    Args:
        idx: Index in the gradient (0 to steps-1)
        steps: Total number of gradient steps
        h1, s1, v1: Start color HSV
        h2, s2, v2: End color HSV
        fine_shade1, fine_shade2: Fine-tune shade adjustments
        fine_hue2: Fine-tune hue adjustment for end color
        gradient_curve: Curve adjustment value
        shade: Overall shade value
        levels: Number of color levels
    
    Returns:
        Dictionary with color information
    """
    v1_adjusted = shade * fine_shade1
    v2_adjusted = shade * fine_shade2
    h2_adjusted = (h2 + fine_hue2) % 1.0
    
    t = idx / (steps - 1) if steps > 1 else 0
    t_curve = curve_t(t, gradient_curve)
    
    dh = ((h2_adjusted - h1 + 1.5) % 1.0) - 0.5
    h = (h1 + t_curve * dh) % 1.0
    s = s1 + t_curve * (s2 - s1)
    v = v1_adjusted + t_curve * (v2_adjusted - v1_adjusted)
    
    return get_color_info(h, s, v, levels)
