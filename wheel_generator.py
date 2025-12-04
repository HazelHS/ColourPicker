"""
Color wheel image generation using numpy for performance.
"""
import numpy as np
from PIL import Image


def quantize_array(arr, levels):
    """
    Quantize an RGB numpy array (H x W x 3) according to numeric levels.
    levels: int (1..65536). If levels >= 256, return arr unchanged (8-bit channels).
    """
    if levels is None or levels >= 256:
        return arr
    if levels <= 1:
        # map everything to mid-grey for extreme quantization
        return np.full_like(arr, 128, dtype=np.uint8)

    step = 255.0 / (levels - 1)
    quantized = np.round(arr.astype(np.float32) / step) * step
    return np.clip(quantized, 0, 255).astype(np.uint8)


def generate_colour_wheel(size=300, hue_shift=0.0, shade=1.0, levels=65536):
    """
    Generate a color wheel image with an optional quantization level (1..65536).
    
    Args:
        size: Width and height of the image in pixels
        hue_shift: Rotation of hue values (0-1)
        shade: Overall brightness/value (0-1)
        levels: Quantization level (1..65536)
    
    Returns:
        PIL Image object of the color wheel
    """
    # Optimized: Use numpy for vectorized operations
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    center = size // 2
    radius = size // 2 - 2
    y_indices, x_indices = np.ogrid[:size, :size]
    dx = x_indices - center
    dy = y_indices - center
    r = np.sqrt(dx**2 + dy**2)
    mask = r <= radius
    angle = (np.arctan2(dy, dx) + np.pi) / (2 * np.pi)
    shifted_angle = (angle + hue_shift) % 1.0
    s = np.clip(r / radius, 0, 1)

    # Vectorized HSV to RGB conversion
    h = shifted_angle[mask].flatten()
    s_masked = s[mask].flatten()
    v_arr = np.full_like(h, shade)
    
    # Manual HSV to RGB conversion (faster than vectorized colorsys)
    h_i = (h * 6).astype(int)
    f = h * 6 - h_i
    p = v_arr * (1 - s_masked)
    q = v_arr * (1 - f * s_masked)
    t = v_arr * (1 - (1 - f) * s_masked)
    
    r_vals = np.choose(h_i % 6, [v_arr, q, p, p, t, v_arr])
    g_vals = np.choose(h_i % 6, [t, v_arr, v_arr, q, p, p])
    b_vals = np.choose(h_i % 6, [p, p, t, v_arr, v_arr, q])
    
    arr[mask, 0] = (r_vals * 255).astype(np.uint8)
    arr[mask, 1] = (g_vals * 255).astype(np.uint8)
    arr[mask, 2] = (b_vals * 255).astype(np.uint8)
    
    # Apply quantization if requested (effective only when levels < 256)
    if levels is not None and levels < 256:
        arr = quantize_array(arr, levels)

    img = Image.fromarray(arr, "RGB")
    return img
