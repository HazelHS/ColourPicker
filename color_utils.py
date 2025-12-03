"""
Color utility functions for RGB/HSV/Hex conversions and color naming.
"""
import colorsys
import math

# Global color dictionary and cache
_colour_dict = {}
COLOR_CACHE = {}


def init_color_dict():
    """Initialize the color name dictionary with web colors."""
    global _colour_dict
    _colour_dict = {
        "aliceblue": (240, 248, 255),
        "antiquewhite": (250, 235, 210),
        "aqua": (0, 255, 255),
        "aquamarine": (127, 255, 212),
        "azure": (240, 255, 255),
        "beige": (245, 245, 220),
        "bisque": (255, 228, 196),
        "black": (0, 0, 0),
        "blanchedalmond": (255, 235, 205),
        "blue": (0, 0, 255),
        "blueviolet": (138, 43, 226),
        "brown": (165, 42, 42),
        "burlywood": (222, 184, 135),
        "cadetblue": (95, 158, 160),
        "chartreuse": (127, 255, 0),
        "chocolate": (210, 105, 30),
        "coral": (255, 127, 80),
        "cornflowerblue": (100, 149, 237),
        "cornsilk": (255, 248, 220),
        "crimson": (220, 20, 60),
        "cyan": (0, 255, 255),
        "darkblue": (0, 0, 139),
        "darkcyan": (0, 139, 139),
        "darkgoldenrod": (184, 134, 11),
        "darkgray": (169, 169, 169),
        "darkgreen": (0, 100, 0),
        "darkkhaki": (189, 183, 107),
        "darkmagenta": (139, 0, 139),
        "darkolivegreen": (85, 107, 47),
        "darkorange": (255, 140, 0),
        "darkorchid": (153, 50, 204),
        "darkred": (139, 0, 0),
        "darksalmon": (233, 150, 122),
        "darkseagreen": (143, 188, 143),
        "darkslateblue": (72, 61, 139),
        "darkslategray": (47, 79, 79),
        "darkturquoise": (0, 206, 209),
        "darkviolet": (148, 0, 211),
        "deeppink": (255, 20, 147),
        "deepskyblue": (0, 191, 255),
        "dimgray": (105, 105, 105),
        "dodgerblue": (30, 144, 255),
        "firebrick": (178, 34, 34),
        "floralwhite": (255, 250, 240),
        "forestgreen": (34, 139, 34),
        "fuchsia": (255, 0, 255),
        "gainsboro": (220, 220, 220),
        "ghostwhite": (248, 248, 255),
        "gold": (255, 215, 0),
        "goldenrod": (218, 165, 32),
        "gray": (128, 128, 128),
        "green": (0, 128, 0),
        "greenyellow": (173, 255, 47),
        "honeydew": (240, 255, 240),
        "hotpink": (255, 105, 180),
        "indianred": (205, 92, 92),
        "indigo": (75, 0, 130),
        "ivory": (255, 255, 240),
        "khaki": (240, 230, 140),
        "lavender": (230, 230, 250),
        "lavenderblush": (255, 240, 245),
        "lawngreen": (124, 252, 0),
        "lemonchiffon": (255, 250, 205),
        "lightblue": (173, 216, 230),
        "lightcoral": (240, 128, 128),
        "lightcyan": (224, 255, 255),
        "lightgoldenrodyellow": (250, 250, 210),
        "lightgray": (211, 211, 211),
        "lightgreen": (144, 238, 144),
        "lightpink": (255, 182, 193),
        "lightsalmon": (255, 160, 122),
        "lightseagreen": (32, 178, 170),
        "lightskyblue": (135, 206, 250),
        "lightslategray": (119, 136, 153),
        "lightsteelblue": (176, 196, 222),
        "lightyellow": (255, 255, 224),
        "lime": (0, 255, 0),
        "limegreen": (50, 205, 50),
        "linen": (250, 240, 230),
        "magenta": (255, 0, 255),
        "maroon": (128, 0, 0),
        "mediumaquamarine": (102, 205, 170),
        "mediumblue": (0, 0, 205),
        "mediumorchid": (186, 85, 211),
        "mediumpurple": (147, 112, 219),
        "mediumseagreen": (60, 179, 113),
        "mediumslateblue": (123, 104, 238),
        "mediumspringgreen": (0, 250, 154),
        "mediumturquoise": (72, 209, 204),
        "mediumvioletred": (199, 21, 133),
        "midnightblue": (25, 25, 112),
        "mintcream": (245, 255, 250),
        "mistyrose": (255, 228, 225),
        "moccasin": (255, 228, 181),
        "navajowhite": (255, 222, 173),
        "navy": (0, 0, 128),
        "oldlace": (253, 245, 230),
        "olive": (128, 128, 0),
        "olivedrab": (107, 142, 35),
        "orange": (255, 165, 0),
        "orangered": (255, 69, 0),
        "orchid": (218, 112, 214),
        "palegoldenrod": (238, 232, 170),
        "palegreen": (152, 251, 152),
        "paleturquoise": (175, 238, 238),
        "palevioletred": (219, 112, 147),
        "papayawhip": (255, 239, 213),
        "peachpuff": (255, 218, 185),
        "peru": (205, 133, 63),
        "pink": (255, 192, 203),
        "plum": (221, 160, 221),
        "powderblue": (176, 224, 230),
        "purple": (128, 0, 128),
        "rebeccapurple": (102, 51, 153),
        "red": (255, 0, 0),
        "rosybrown": (188, 143, 143),
        "royalblue": (65, 105, 225),
        "saddlebrown": (139, 69, 19),
        "salmon": (250, 128, 114),
        "sandybrown": (244, 164, 96),
        "seagreen": (46, 139, 87),
        "seashell": (255, 245, 238),
        "sienna": (160, 82, 45),
        "silver": (192, 192, 192),
        "skyblue": (135, 206, 235),
        "slateblue": (106, 90, 205),
        "slategray": (112, 128, 144),
        "snow": (255, 250, 250),
        "springgreen": (0, 255, 127),
        "steelblue": (70, 130, 180),
        "tan": (210, 180, 140),
        "teal": (0, 128, 128),
        "thistle": (216, 191, 216),
        "tomato": (255, 99, 71),
        "turquoise": (64, 224, 208),
        "violet": (238, 130, 238),
        "wheat": (245, 222, 179),
        "white": (255, 255, 255),
        "whitesmoke": (245, 245, 245),
        "yellow": (255, 255, 0),
        "yellowgreen": (154, 205, 50),
    }


def closest_colour(requested_colour):
    """
    Find the closest named color to the requested RGB color.
    
    Args:
        requested_colour: Tuple of (r, g, b) values (0-255)
    
    Returns:
        Name of the closest color
    """
    # Check cache first
    cache_key = requested_colour
    if cache_key in COLOR_CACHE:
        return COLOR_CACHE[cache_key]
    
    min_dist = float('inf')
    closest_name = "unknown"
    for name, (r_c, g_c, b_c) in _colour_dict.items():
        dist = (r_c - requested_colour[0]) ** 2 + (g_c - requested_colour[1]) ** 2 + (b_c - requested_colour[2]) ** 2
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            if dist == 0:  # Exact match
                break
    
    COLOR_CACHE[cache_key] = closest_name
    return closest_name


def get_colour_name(rgb):
    """
    Get the name of a color from its RGB values.
    
    Args:
        rgb: Tuple of (r, g, b) values (0-255)
    
    Returns:
        Name of the color (exact match or closest approximation)
    """
    # Check cache first
    if rgb in COLOR_CACHE:
        return COLOR_CACHE[rgb]
    
    # Try to find an exact match
    for name, color_rgb in _colour_dict.items():
        if color_rgb == rgb:
            COLOR_CACHE[rgb] = name
            return name
    
    return closest_colour(rgb)


def hsv_to_rgb255(h, s, v):
    """
    Convert HSV color to RGB (0-255 range).
    
    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value/Brightness (0-1)
    
    Returns:
        Tuple of (r, g, b) values (0-255)
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def rgb_to_hsv(r, g, b):
    """
    Convert RGB (0-255) to HSV (0-1).
    
    Args:
        r, g, b: RGB values (0-255)
    
    Returns:
        Tuple of (h, s, v) values (0-1)
    """
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


def rgb_to_hex(rgb):
    """
    Convert RGB tuple to hex color string.
    
    Args:
        rgb: Tuple of (r, g, b) values (0-255)
    
    Returns:
        Hex color string (e.g., '#ff0000')
    """
    return '#%02x%02x%02x' % rgb


def hex_to_rgb(hex_str):
    """
    Convert hex color string to RGB tuple.
    
    Args:
        hex_str: Hex color string (with or without '#')
    
    Returns:
        Tuple of (r, g, b) values (0-255) or None if invalid
    """
    hex_str = hex_str.strip()
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]
    
    if len(hex_str) != 6:
        return None
    
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def calculate_opposite_hue(h):
    """
    Calculate the opposite hue on the color wheel.
    
    Args:
        h: Hue value (0-1)
    
    Returns:
        Opposite hue value (0-1)
    """
    return (h + 0.5) % 1.0


def get_color_info(h, s, v):
    """
    Get complete color information for an HSV color.
    
    Args:
        h, s, v: HSV values (0-1)
    
    Returns:
        Dictionary with rgb, hex, name, opp_h, opp_rgb, opp_hex, opp_name
    """
    rgb = hsv_to_rgb255(h, s, v)
    hex_code = rgb_to_hex(rgb)
    name = get_colour_name(rgb)
    
    opp_h = calculate_opposite_hue(h)
    opp_rgb = hsv_to_rgb255(opp_h, s, v)
    opp_hex = rgb_to_hex(opp_rgb)
    opp_name = get_colour_name(opp_rgb)
    
    return {
        'rgb': rgb,
        'hex': hex_code,
        'name': name,
        'opp_h': opp_h,
        'opp_rgb': opp_rgb,
        'opp_hex': opp_hex,
        'opp_name': opp_name
    }
