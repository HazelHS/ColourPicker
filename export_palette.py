import os
import tkinter.filedialog as fd
from color_utils import hsv_to_rgb255, get_colour_name

def export_palette(
    gradient_steps,
    gradient_curve,
    fine_shade1,
    fine_shade2,
    fine_hue2,
    shade,
    hue_shift,
    selected_h,
    selected_s,
    selected_v,
    selected_opp_h,
):
    """Export current gradient as a GIMP palette file (.gpl)."""
    file_path = fd.asksaveasfilename(
        defaultextension=".gpl",
        filetypes=[("GIMP Palette", "*.gpl")],
        title="Save Palette As"
    )
    if not file_path:
        return

    palette_name = os.path.splitext(os.path.basename(file_path))[0]

    lines = [
        "GIMP Palette",
        f"Name: {palette_name}",
        "#"
    ]
    steps = int(gradient_steps)

    # Use selected color or default
    if selected_h is not None and selected_s is not None and selected_v is not None:
        h1, s1, v1 = selected_h, selected_s, selected_v
        h2, s2, v2 = selected_opp_h, selected_s, selected_v
    else:
        h1 = (0 + hue_shift) % 1.0
        s1 = 1
        v1 = shade
        h2 = (h1 + 0.5) % 1.0
        s2 = 1
        v2 = shade

    # Apply fine-tune adjustments (multiply, don't replace)
    v1 = v1 * fine_shade1
    v2 = v2 * fine_shade2
    h2 = (h2 + fine_hue2) % 1.0

    def curve_t(t, curve):
        c = curve / 100.0
        if c == 0:
            return t
        elif c > 0:
            return t ** (1 / (1 + c * 2))
        else:
            return t ** (1 - c * 2)

    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        t_curve = curve_t(t, gradient_curve)
        dh = ((h2 - h1 + 1.5) % 1.0) - 0.5
        h = (h1 + t_curve * dh) % 1.0
        s = s1 + t_curve * (s2 - s1)
        v = v1 + t_curve * (v2 - v1)
        rgb = hsv_to_rgb255(h, s, v)
        name = get_colour_name(rgb)
        lines.append(f"{rgb[0]:3d} {rgb[1]:3d} {rgb[2]:3d} {name}")

    with open(file_path, "w") as f:
        f.write("\n".join(lines))