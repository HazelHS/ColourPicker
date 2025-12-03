import os
import tkinter.filedialog as fd
from color_utils import rgb_to_hex, get_colour_name
from gradient_logic import calculate_gradient_colors

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

    # Use the same gradient logic as the GUI
    colors = calculate_gradient_colors(
        steps, h1, s1, v1, h2, s2, v2,
        fine_shade1, fine_shade2, fine_hue2,
        gradient_curve, shade
    )

    for rgb in colors:
        name = get_colour_name(rgb)
        lines.append(f"{rgb[0]:3d} {rgb[1]:3d} {rgb[2]:3d} {name}")

    with open(file_path, "w") as f:
        f.write("\n".join(lines))