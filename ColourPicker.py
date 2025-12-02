import tkinter as tk
from tkinter import Canvas, Label
from PIL import Image, ImageTk
import colorsys
import math
import matplotlib.colors as mcolors
import tkinter.filedialog as fd
import numpy as np

# Cache color names lookup for performance
COLOR_CACHE = {}
CSS4_COLORS_DICT = {}

def init_color_dict():
    global CSS4_COLORS_DICT
    if not CSS4_COLORS_DICT:
        for name, hex_value in mcolors.CSS4_COLORS.items():
            r_c, g_c, b_c = mcolors.to_rgb(hex_value)
            r_c, g_c, b_c = int(r_c * 255), int(g_c * 255), int(b_c * 255)
            CSS4_COLORS_DICT[name] = (r_c, g_c, b_c)

def closest_colour(requested_colour):
    # Check cache first
    cache_key = requested_colour
    if cache_key in COLOR_CACHE:
        return COLOR_CACHE[cache_key]
    
    min_dist = float('inf')
    closest_name = "unknown"
    for name, (r_c, g_c, b_c) in CSS4_COLORS_DICT.items():
        dist = (r_c - requested_colour[0]) ** 2 + (g_c - requested_colour[1]) ** 2 + (b_c - requested_colour[2]) ** 2
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            if dist == 0:  # Exact match
                break
    
    COLOR_CACHE[cache_key] = closest_name
    return closest_name

def get_colour_name(rgb):
    # Check cache first
    if rgb in COLOR_CACHE:
        return COLOR_CACHE[rgb]
    
    # Try to find an exact match
    for name, color_rgb in CSS4_COLORS_DICT.items():
        if color_rgb == rgb:
            COLOR_CACHE[rgb] = name
            return name
    
    return closest_colour(rgb)

def hsv_to_rgb255(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def generate_colour_wheel(size=300, hue_shift=0.0, shade=1.0):
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

    img = Image.fromarray(arr, "RGB")
    return img

class ColourWheelApp:
    def __init__(self, root):
        init_color_dict()
        
        self.size = 300
        self.root = root
        self.root.title("Colour Wheel Picker")
        self.hue_shift = 0.0
        self.shade = 1.0

        # Standard slider length for main controls
        MAIN_SLIDER_LENGTH = 400

        # Hue slider with entry and reset
        hue_frame = tk.Frame(root)
        hue_frame.pack(fill="x")
        self.hue_slider = tk.Scale(hue_frame, from_=0, to=360, orient="horizontal", label="Hue", resolution=0.001, length=MAIN_SLIDER_LENGTH)
        self.hue_slider.pack(side="left", fill="x", expand=True)
        self.hue_entry = tk.Entry(hue_frame, width=10)
        self.hue_entry.pack(side="left", padx=2)
        self.hue_entry.insert(0, "0.000")
        self.hue_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.hue_slider, self.hue_entry, 0, 360))
        self.hue_slider.config(command=lambda v: [self.update_entry(self.hue_entry, v), self.on_slider()])
        self.hue_reset_btn = tk.Button(hue_frame, text="Reset", command=lambda: self.reset_slider(self.hue_slider, 0))
        self.hue_reset_btn.pack(side="left", padx=2)

        # Shade slider with entry and reset
        shade_frame = tk.Frame(root)
        shade_frame.pack(fill="x")
        self.shade_slider = tk.Scale(shade_frame, from_=0, to=100, orient="horizontal", label="Shade (Light/Dark)", resolution=0.001, length=MAIN_SLIDER_LENGTH)
        self.shade_slider.set(100)
        self.shade_slider.pack(side="left", fill="x", expand=True)
        self.shade_entry = tk.Entry(shade_frame, width=10)
        self.shade_entry.pack(side="left", padx=2)
        self.shade_entry.insert(0, "100.000")
        self.shade_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.shade_slider, self.shade_entry, 0, 100))
        self.shade_slider.config(command=lambda v: [self.update_entry(self.shade_entry, v), self.on_slider()])
        self.shade_reset_btn = tk.Button(shade_frame, text="Reset", command=lambda: self.reset_slider(self.shade_slider, 100))
        self.shade_reset_btn.pack(side="left", padx=2)

        # Interval slider with entry and reset
        interval_frame = tk.Frame(root)
        interval_frame.pack(fill="x")
        self.interval_slider = tk.Scale(interval_frame, from_=2, to=50, orient="horizontal", label="Gradient Steps", resolution=1, length=MAIN_SLIDER_LENGTH)
        self.interval_slider.set(20)
        self.interval_slider.pack(side="left", fill="x", expand=True)
        self.interval_entry = tk.Entry(interval_frame, width=10)
        self.interval_entry.pack(side="left", padx=2)
        self.interval_entry.insert(0, "20")
        self.interval_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.interval_slider, self.interval_entry, 2, 50))
        self.interval_slider.config(command=lambda v: [self.update_entry(self.interval_entry, v), self.on_interval_slider()])
        self.interval_reset_btn = tk.Button(interval_frame, text="Reset", command=lambda: self.reset_slider(self.interval_slider, 20))
        self.interval_reset_btn.pack(side="left", padx=2)

        # Curve slider with entry and reset
        curve_frame = tk.Frame(root)
        curve_frame.pack(fill="x")
        self.curve_slider = tk.Scale(curve_frame, from_=-100, to=100, orient="horizontal", label="Gradient Curve", resolution=0.001, length=MAIN_SLIDER_LENGTH)
        self.curve_slider.set(0)
        self.curve_slider.pack(side="left", fill="x", expand=True)
        self.curve_entry = tk.Entry(curve_frame, width=10)
        self.curve_entry.pack(side="left", padx=2)
        self.curve_entry.insert(0, "0.000")
        self.curve_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.curve_slider, self.curve_entry, -100, 100))
        self.curve_slider.config(command=lambda v: [self.update_entry(self.curve_entry, v), self.on_curve_slider()])
        self.curve_reset_btn = tk.Button(curve_frame, text="Reset", command=lambda: self.reset_slider(self.curve_slider, 0))
        self.curve_reset_btn.pack(side="left", padx=2)

        # Fine Tune frame
        fine_tune_frame = tk.LabelFrame(root, text="Fine Tune", padx=4, pady=4)
        fine_tune_frame.pack(fill="x", pady=2)

        # Start Shade slider with entry and reset
        start_shade_frame = tk.Frame(fine_tune_frame)
        start_shade_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.fine_shade1_slider = tk.Scale(start_shade_frame, from_=0, to=100, orient="horizontal", label="Start Shade", resolution=0.001, length=200)
        self.fine_shade1_slider.set(100)
        self.fine_shade1_slider.pack(side="left")
        self.fine_shade1_entry = tk.Entry(start_shade_frame, width=10)
        self.fine_shade1_entry.pack(side="left", padx=2)
        self.fine_shade1_entry.insert(0, "100.000")
        self.fine_shade1_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.fine_shade1_slider, self.fine_shade1_entry, 0, 100))
        self.fine_shade1_slider.config(command=lambda v: [self.update_entry(self.fine_shade1_entry, v), self.on_fine_slider()])
        self.fine_shade1_reset_btn = tk.Button(start_shade_frame, text="Reset", command=lambda: self.reset_slider(self.fine_shade1_slider, 100))
        self.fine_shade1_reset_btn.pack(side="left", padx=2)

        # End Shade slider with entry and reset
        end_shade_frame = tk.Frame(fine_tune_frame)
        end_shade_frame.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self.fine_shade2_slider = tk.Scale(end_shade_frame, from_=0, to=100, orient="horizontal", label="End Shade", resolution=0.001, length=200)
        self.fine_shade2_slider.set(100)
        self.fine_shade2_slider.pack(side="left")
        self.fine_shade2_entry = tk.Entry(end_shade_frame, width=10)
        self.fine_shade2_entry.pack(side="left", padx=2)
        self.fine_shade2_entry.insert(0, "100.000")
        self.fine_shade2_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.fine_shade2_slider, self.fine_shade2_entry, 0, 100))
        self.fine_shade2_slider.config(command=lambda v: [self.update_entry(self.fine_shade2_entry, v), self.on_fine_slider()])
        self.fine_shade2_reset_btn = tk.Button(end_shade_frame, text="Reset", command=lambda: self.reset_slider(self.fine_shade2_slider, 100))
        self.fine_shade2_reset_btn.pack(side="left", padx=2)

        # End Hue Shift slider with entry and reset (full width)
        end_hue_frame = tk.Frame(fine_tune_frame)
        end_hue_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
        self.fine_hue2_slider = tk.Scale(end_hue_frame, from_=-180, to=180, orient="horizontal", label="End Hue Shift", resolution=0.001, length=500)
        self.fine_hue2_slider.set(0)
        self.fine_hue2_slider.pack(side="left")
        self.fine_hue2_entry = tk.Entry(end_hue_frame, width=10)
        self.fine_hue2_entry.pack(side="left", padx=2)
        self.fine_hue2_entry.insert(0, "0.000")
        self.fine_hue2_entry.bind("<Return>", lambda e: self.set_slider_from_entry(self.fine_hue2_slider, self.fine_hue2_entry, -180, 180))
        self.fine_hue2_slider.config(command=lambda v: [self.update_entry(self.fine_hue2_entry, v), self.on_fine_slider()])
        self.fine_hue2_reset_btn = tk.Button(end_hue_frame, text="Reset", command=lambda: self.reset_slider(self.fine_hue2_slider, 0))
        self.fine_hue2_reset_btn.pack(side="left", padx=2)

        # Configure grid weights for fine tune frame
        fine_tune_frame.grid_columnconfigure(0, weight=1)
        fine_tune_frame.grid_columnconfigure(1, weight=1)

        self.img = generate_colour_wheel(self.size, self.hue_shift, self.shade)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas = Canvas(root, width=self.size, height=self.size)
        self.canvas.pack()
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        # Replace Label with Text widget
        self.text = tk.Text(root, height=2, font=("Arial", 12), wrap="none")
        self.text.pack(fill="x")
        self.text.config(state="disabled")
        self.locked = False
        self.last_event = None
        self.last_panel = "wheel"
        self.last_square_idx = None
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.toggle_lock)

        # Gradient squares panel
        self.squares_frame = tk.Frame(root)
        self.squares_frame.pack(fill="x")
        self.squares = []
        self.square_size = 24
        self.gradient_steps = int(self.interval_slider.get())
        self.selected_h = None
        self.selected_s = None
        self.selected_v = None
        self.selected_rgb = None
        self.selected_opp_h = None
        self.selected_opp_rgb = None
        self.gradient_curve = 0
        self.fine_shade1 = 1.0
        self.fine_shade2 = 1.0
        self.fine_hue2 = 0.0
        
        # Debounce timer for populate_squares
        self.populate_timer = None
        
        self.populate_squares()

        # Export button
        self.export_btn = tk.Button(root, text="Export Palette (.gpl)", command=self.export_palette)
        self.export_btn.pack(pady=8)

    def on_slider(self, event=None):
        self.hue_shift = self.hue_slider.get() / 360.0
        self.shade = self.shade_slider.get() / 100.0
        self.img = generate_colour_wheel(self.size, self.hue_shift, self.shade)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)
        self.schedule_populate_squares()
        if self.last_event and self.last_panel == "wheel":
            self.on_mouse_move(self.last_event)
        elif self.last_square_idx is not None and self.last_panel == "squares":
            self.on_square_hover(self.last_square_idx)
        self.selected_h = None
        self.selected_s = None
        self.selected_v = None
        self.selected_rgb = None
        self.selected_opp_h = None
        self.selected_opp_rgb = None

    def schedule_populate_squares(self):
        # Debounce: only call populate_squares after slider stops moving for 50ms
        if self.populate_timer:
            self.root.after_cancel(self.populate_timer)
        self.populate_timer = self.root.after(50, self.populate_squares)

    def on_interval_slider(self, event=None):
        self.gradient_steps = int(self.interval_slider.get())
        self.schedule_populate_squares()
        if self.locked and self.last_panel == "squares" and self.last_square_idx is not None:
            self.on_square_hover(self.last_square_idx)

    def on_curve_slider(self, event=None):
        self.gradient_curve = self.curve_slider.get()
        self.schedule_populate_squares()
        # If locked on a square, refresh its info
        if self.locked and self.last_panel == "squares" and self.last_square_idx is not None:
            self.on_square_hover(self.last_square_idx)

    def on_fine_slider(self, event=None):
        self.fine_shade1 = self.fine_shade1_slider.get() / 100.0
        self.fine_shade2 = self.fine_shade2_slider.get() / 100.0
        self.fine_hue2 = self.fine_hue2_slider.get() / 360.0  # -0.5 to +0.5
        self.schedule_populate_squares()
        # If locked on a square, refresh its info
        if self.locked and self.last_panel == "squares" and self.last_square_idx is not None:
            self.on_square_hover(self.last_square_idx)

    def reset_slider(self, slider, value):
        slider.set(value)
        # Call appropriate update function
        if slider in [self.hue_slider, self.shade_slider]:
            self.on_slider()
        elif slider == self.interval_slider:
            self.on_interval_slider()
        elif slider == self.curve_slider:
            self.on_curve_slider()
        elif slider in [self.fine_shade1_slider, self.fine_shade2_slider, self.fine_hue2_slider]:
            self.on_fine_slider()

    def toggle_lock(self, event):
        # If mouse is over a square, lock that square
        if hasattr(self, "hovered_square_idx") and self.hovered_square_idx is not None:
            self.locked = not self.locked
            if self.locked:
                self.last_panel = "squares"
                self.last_square_idx = self.hovered_square_idx
            else:
                self.last_panel = "wheel"
                self.last_square_idx = None
        else:
            self.locked = not self.locked
            if self.locked:
                self.last_panel = "wheel"
            else:
                self.last_panel = "wheel"
                self.last_square_idx = None

    def on_mouse_move(self, event):
        self.last_event = event
        self.hovered_square_idx = None
        if self.locked and self.last_panel == "squares":
            return
        if self.locked and self.last_panel == "wheel":
            return
        x, y = event.x, event.y
        center = self.size // 2
        dx = x - center
        dy = y - center
        r = math.sqrt(dx*dx + dy*dy)
        radius = self.size // 2 - 2
        if 0 <= x < self.size and 0 <= y < self.size and r <= radius:
            angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            shifted_angle = (angle + self.hue_shift) % 1.0
            s = r / radius
            v = self.shade
            rgb = hsv_to_rgb255(shifted_angle, s, v)
            hex_code = rgb_to_hex(rgb)
            name = get_colour_name(rgb)
            opp_angle = (shifted_angle + 0.5) % 1.0
            opp_rgb = hsv_to_rgb255(opp_angle, s, v)
            opp_hex = rgb_to_hex(opp_rgb)
            opp_name = get_colour_name(opp_rgb)
            text = (
                f"Colour: {hex_code} {rgb} {name}\n"
                f"Opposite: {opp_hex} {opp_rgb} {opp_name}"
            )
            self.text.config(state="normal")
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, text)
            self.text.config(state="disabled")
            self.last_panel = "wheel"
            self.last_square_idx = None
            # Store for gradient
            self.selected_h = shifted_angle
            self.selected_s = s
            self.selected_v = v
            self.selected_rgb = rgb
            self.selected_opp_h = opp_angle
            self.selected_opp_rgb = opp_rgb
            self.schedule_populate_squares()
        else:
            self.text.config(state="normal")
            self.text.delete("1.0", tk.END)
            self.text.config(state="disabled")

    def curve_t(self, t, curve):
        # Curve: -100 (start) to 0 (linear) to +100 (end)
        c = curve / 100.0
        if c == 0:
            return t
        elif c > 0:
            return t ** (1 / (1 + c * 2))  # weight toward end
        else:
            return t ** (1 - c * 2)        # weight toward start

    def populate_squares(self):
        # Remove old squares
        for widget in self.squares_frame.winfo_children():
            widget.destroy()
        self.squares = []
        steps = int(self.gradient_steps)

        # Use selected colour and its opposite from the wheel, or default to wheel center
        if self.selected_h is not None and self.selected_s is not None and self.selected_v is not None:
            h1, s1, v1 = self.selected_h, self.selected_s, self.selected_v
            h2, s2 = self.selected_opp_h, self.selected_s
            v2 = self.selected_v
        else:
            h1 = (0 + self.hue_shift) % 1.0
            s1 = 1
            v1 = self.shade
            h2 = (h1 + 0.5) % 1.0
            s2 = 1
            v2 = self.shade

        # Apply global shade, then fine tune shades (multiply to combine effects)
        v1 = self.shade * self.fine_shade1
        v2 = self.shade * self.fine_shade2
        # Fine tune hue for end colour
        h2 = (h2 + self.fine_hue2) % 1.0

        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            t_curve = self.curve_t(t, self.gradient_curve)
            # Interpolate hue circularly
            dh = ((h2 - h1 + 1.5) % 1.0) - 0.5
            h = (h1 + t_curve * dh) % 1.0
            s = s1 + t_curve * (s2 - s1)
            v = v1 + t_curve * (v2 - v1)
            rgb = hsv_to_rgb255(h, s, v)
            hex_code = rgb_to_hex(rgb)
            square = tk.Label(self.squares_frame, bg=hex_code, width=2, height=1, relief="raised", borderwidth=2)
            square.grid(row=0, column=i, padx=1, pady=2)
            square.bind("<Enter>", lambda e, idx=i: self.on_square_hover(idx))
            square.bind("<Button-1>", lambda e, idx=i: self.on_square_click(idx))
            self.squares.append(square)

    def on_square_hover(self, idx):
        if self.locked and self.last_panel == "wheel":
            return
        self.hovered_square_idx = idx
        steps = int(self.gradient_steps)

        # Use selected colour and its opposite from the wheel, or default to wheel center
        if self.selected_h is not None and self.selected_s is not None and self.selected_v is not None:
            h1, s1, v1 = self.selected_h, self.selected_s, self.selected_v
            h2, s2 = self.selected_opp_h, self.selected_s
            v2 = self.selected_v
        else:
            h1 = (0 + self.hue_shift) % 1.0
            s1 = 1
            v1 = self.shade
            h2 = (h1 + 0.5) % 1.0
            s2 = 1
            v2 = self.shade

        # Apply global shade, then fine tune shades
        v1 = self.shade * self.fine_shade1
        v2 = self.shade * self.fine_shade2
        h2 = (h2 + self.fine_hue2) % 1.0

        t = idx / (steps - 1) if steps > 1 else 0
        t_curve = self.curve_t(t, self.gradient_curve)
        dh = ((h2 - h1 + 1.5) % 1.0) - 0.5
        h = (h1 + t_curve * dh) % 1.0
        s = s1 + t_curve * (s2 - s1)
        v = v1 + t_curve * (v2 - v1)
        rgb = hsv_to_rgb255(h, s, v)
        hex_code = rgb_to_hex(rgb)
        name = get_colour_name(rgb)
        opp_h = (h + 0.5) % 1.0
        opp_rgb = hsv_to_rgb255(opp_h, s, v)
        opp_hex = rgb_to_hex(opp_rgb)
        opp_name = get_colour_name(opp_rgb)
        text = (
            f"Colour: {hex_code} {rgb} {name}\n"
            f"Opposite: {opp_hex} {opp_rgb} {opp_name}"
        )
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state="disabled")
        self.last_panel = "squares"
        self.last_square_idx = idx

    def on_square_click(self, idx):
        if self.locked and self.last_panel == "squares" and self.last_square_idx == idx:
            self.locked = False
            self.last_panel = "wheel"
            self.last_square_idx = None
        else:
            self.locked = True
            self.last_panel = "squares"
            self.last_square_idx = idx
            self.on_square_hover(idx)

    def export_palette(self):
        # Ask for file location
        file_path = fd.asksaveasfilename(
            defaultextension=".gpl",
            filetypes=[("GIMP Palette", "*.gpl")],
            title="Save Palette As"
        )
        if not file_path:
            return

        # Extract filename without extension for palette name
        import os
        palette_name = os.path.splitext(os.path.basename(file_path))[0]

        lines = [
            "GIMP Palette",
            f"Name: {palette_name}",
            "#"
        ]
        steps = int(self.gradient_steps)

        # Use selected colour and its opposite from the wheel, or default to wheel center
        if self.selected_h is not None and self.selected_s is not None and self.selected_v is not None:
            h1, s1, v1 = self.selected_h, self.selected_s, self.selected_v
            h2, s2 = self.selected_opp_h, self.selected_s
            v2 = self.selected_v
        else:
            h1 = (0 + self.hue_shift) % 1.0
            s1 = 1
            v1 = self.shade
            h2 = (h1 + 0.5) % 1.0
            s2 = 1
            v2 = self.shade

        v1 = self.shade * self.fine_shade1
        v2 = self.shade * self.fine_shade2
        h2 = (h2 + self.fine_hue2) % 1.0

        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            t_curve = self.curve_t(t, self.gradient_curve)
            dh = ((h2 - h1 + 1.5) % 1.0) - 0.5
            h = (h1 + t_curve * dh) % 1.0
            s = s1 + t_curve * (s2 - s1)
            v = v1 + t_curve * (v2 - v1)
            rgb = hsv_to_rgb255(h, s, v)
            name = get_colour_name(rgb)
            lines.append(f"{rgb[0]:3d} {rgb[1]:3d} {rgb[2]:3d} {name}")

        with open(file_path, "w") as f:
            f.write("\n".join(lines))

    def update_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, f"{float(value):.3f}")

    def set_slider_from_entry(self, slider, entry, minval, maxval):
        try:
            val = float(entry.get())
            val = max(minval, min(maxval, val))
            slider.set(val)
        except ValueError:
            pass  # Ignore invalid input

if __name__ == "__main__":
    root = tk.Tk()
    app = ColourWheelApp(root)
    root.mainloop()
