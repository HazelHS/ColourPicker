"""
UI component builders for the Color Picker application.
"""
import tkinter as tk

from wheel_generator import generate_colour_wheel
from PIL import ImageTk
from tkinter import Canvas


class SliderWithEntry:
    """A slider with an accompanying entry field and reset button."""
    
    def __init__(self, parent, label, from_val, to_val, default_val, resolution=0.001, length=400):
        """
        Create a slider with entry field and reset button.
        
        Args:
            parent: Parent tkinter widget
            label: Label text for the slider
            from_val: Minimum value
            to_val: Maximum value
            default_val: Default/reset value
            resolution: Step size for slider
            length: Length of slider in pixels
        """
        self.frame = tk.Frame(parent)
        self.from_val = from_val
        self.to_val = to_val
        self.default_val = default_val
        
        self.slider = tk.Scale(
            self.frame, 
            from_=from_val, 
            to=to_val, 
            orient="horizontal", 
            label=label, 
            resolution=resolution, 
            length=length
        )
        self.slider.set(default_val)
        self.slider.pack(side="left", fill="x", expand=True)
        
        self.entry = tk.Entry(self.frame, width=10)
        self.entry.pack(side="left", padx=2)
        self.entry.insert(0, f"{float(default_val):.3f}")
        
        self.reset_btn = tk.Button(self.frame, text="Reset", command=self.reset)
        self.reset_btn.pack(side="left", padx=2)
        
        # Callbacks will be set by parent
        self.on_change_callback = None
        
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame."""
        self.frame.grid(**kwargs)
    
    def set_callbacks(self, slider_callback, entry_callback=None):
        """
        Set callbacks for slider and entry changes.
        
        Args:
            slider_callback: Called when slider value changes
            entry_callback: Called when entry Return is pressed (optional, uses same as slider if None)
        """
        self.on_change_callback = slider_callback
        entry_cb = entry_callback if entry_callback else self._on_entry_return
        
        self.slider.config(command=lambda v: [self._update_entry(v), slider_callback()])
        self.entry.bind("<Return>", lambda e: entry_cb())
    
    def _update_entry(self, value):
        """Update entry field with slider value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{float(value):.3f}")
    
    def _on_entry_return(self):
        """Handle Return key in entry field."""
        try:
            val = float(self.entry.get())
            val = max(self.from_val, min(self.to_val, val))
            self.slider.set(val)
        except ValueError:
            pass  # Ignore invalid input
    
    def reset(self):
        """Reset slider to default value."""
        self.slider.set(self.default_val)
        if self.on_change_callback:
            self.on_change_callback()
    
    def get(self):
        """Get current slider value."""
        return self.slider.get()
    
    def set(self, value):
        """Set slider value."""
        self.slider.set(value)
        self._update_entry(value)


class ColorInputPanel:
    """Panel with RGB and Hex color input fields."""
    
    def __init__(self, parent):
        """
        Create color input panel.
        
        Args:
            parent: Parent tkinter widget
        """
        self.frame = tk.LabelFrame(parent, text="Color Input", padx=4, pady=4)
        
        # RGB inputs
        rgb_frame = tk.Frame(self.frame)
        rgb_frame.pack(side="left", padx=10)
        tk.Label(rgb_frame, text="RGB:").pack(side="left")
        
        self.r_entry = tk.Entry(rgb_frame, width=5)
        self.r_entry.pack(side="left", padx=2)
        self.r_entry.insert(0, "255")
        
        tk.Label(rgb_frame, text=",").pack(side="left")
        
        self.g_entry = tk.Entry(rgb_frame, width=5)
        self.g_entry.pack(side="left", padx=2)
        self.g_entry.insert(0, "0")
        
        tk.Label(rgb_frame, text=",").pack(side="left")
        
        self.b_entry = tk.Entry(rgb_frame, width=5)
        self.b_entry.pack(side="left", padx=2)
        self.b_entry.insert(0, "0")
        
        self.rgb_apply_btn = tk.Button(rgb_frame, text="Apply")
        self.rgb_apply_btn.pack(side="left", padx=4)
        
        # Hex input
        hex_frame = tk.Frame(self.frame)
        hex_frame.pack(side="left", padx=10)
        tk.Label(hex_frame, text="Hex:").pack(side="left")
        
        self.hex_entry = tk.Entry(hex_frame, width=10)
        self.hex_entry.pack(side="left", padx=2)
        self.hex_entry.insert(0, "#ff0000")
        
        self.hex_apply_btn = tk.Button(hex_frame, text="Apply")
        self.hex_apply_btn.pack(side="left", padx=4)
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def set_callbacks(self, rgb_callback, hex_callback):
        """
        Set callbacks for RGB and Hex apply buttons.
        
        Args:
            rgb_callback: Called when RGB apply is clicked
            hex_callback: Called when Hex apply is clicked
        """
        self.rgb_apply_btn.config(command=rgb_callback)
        self.hex_apply_btn.config(command=hex_callback)
        
        self.r_entry.bind("<Return>", lambda e: rgb_callback())
        self.g_entry.bind("<Return>", lambda e: rgb_callback())
        self.b_entry.bind("<Return>", lambda e: rgb_callback())
        self.hex_entry.bind("<Return>", lambda e: hex_callback())
    
    def get_rgb(self):
        """
        Get RGB values from entry fields.
        
        Returns:
            Tuple of (r, g, b) or None if invalid
        """
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())
            
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                return (r, g, b)
        except ValueError:
            pass
        return None
    
    def get_hex(self):
        """
        Get hex value from entry field.
        
        Returns:
            Hex string or None if invalid
        """
        return self.hex_entry.get().strip()
    
    def set_rgb(self, r, g, b):
        """Set RGB entry fields."""
        self.r_entry.delete(0, tk.END)
        self.r_entry.insert(0, str(r))
        self.g_entry.delete(0, tk.END)
        self.g_entry.insert(0, str(g))
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, str(b))
    
    def set_hex(self, hex_str):
        """Set hex entry field."""
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, hex_str)


def create_color_input_panel(app):
    """Create RGB and Hex input panel."""
    app.color_input = ColorInputPanel(app.root)
    app.color_input.pack(fill="x", pady=2)
    app.color_input.set_callbacks(app.apply_rgb_input, app.apply_hex_input)

def create_main_sliders(app, length):
    """Create main control sliders (Hue, Shade, Interval, Curve)."""
    app.hue_slider_widget = SliderWithEntry(
        app.root, "Hue", 0, 360, 0, resolution=0.001, length=length
    )
    app.hue_slider_widget.pack(fill="x")
    app.hue_slider_widget.set_callbacks(app.on_slider)

    app.shade_slider_widget = SliderWithEntry(
        app.root, "Shade (Light/Dark)", 0, 100, 100, resolution=0.001, length=length
    )
    app.shade_slider_widget.pack(fill="x")
    app.shade_slider_widget.set_callbacks(app.on_slider)

    app.interval_slider_widget = SliderWithEntry(
        app.root, "Gradient Steps", 2, 50, 20, resolution=1, length=length
    )
    app.interval_slider_widget.pack(fill="x")
    app.interval_slider_widget.set_callbacks(app.on_interval_slider)

    app.curve_slider_widget = SliderWithEntry(
        app.root, "Gradient Curve", -100, 100, 0, resolution=0.001, length=length
    )
    app.curve_slider_widget.pack(fill="x")
    app.curve_slider_widget.set_callbacks(app.on_curve_slider)

def create_fine_tune_panel(app):
    """Create fine-tune control panel."""
    fine_tune_frame = tk.LabelFrame(app.root, text="Fine Tune", padx=4, pady=4)
    fine_tune_frame.pack(fill="x", pady=2)

    app.fine_shade1_widget = SliderWithEntry(
        fine_tune_frame, "Start Shade", 0, 100, 100, resolution=0.001, length=200
    )
    app.fine_shade1_widget.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
    app.fine_shade1_widget.set_callbacks(app.on_fine_slider)

    app.fine_shade2_widget = SliderWithEntry(
        fine_tune_frame, "End Shade", 0, 100, 100, resolution=0.001, length=200
    )
    app.fine_shade2_widget.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
    app.fine_shade2_widget.set_callbacks(app.on_fine_slider)

    app.fine_hue2_widget = SliderWithEntry(
        fine_tune_frame, "End Hue Shift", -180, 180, 0, resolution=0.001, length=500
    )
    app.fine_hue2_widget.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
    app.fine_hue2_widget.set_callbacks(app.on_fine_slider)

    fine_tune_frame.grid_columnconfigure(0, weight=1)
    fine_tune_frame.grid_columnconfigure(1, weight=1)

def create_color_wheel(app):
    """Create the color wheel canvas."""
    app.img = generate_colour_wheel(app.size, app.hue_shift, app.shade)
    app.tk_img = ImageTk.PhotoImage(app.img)
    app.canvas = Canvas(app.root, width=app.size, height=app.size)
    app.canvas.pack()
    app.canvas_image = app.canvas.create_image(0, 0, anchor=tk.NW, image=app.tk_img)
    app.canvas.bind("<Motion>", app.on_mouse_move)
    app.canvas.bind("<Button-1>", app.toggle_lock)

def create_text_display(app):
    """Create text display for color information."""
    app.text = tk.Text(app.root, height=2, font=("Arial", 12), wrap="none")
    app.text.pack(fill="x")
    app.text.config(state="disabled")

def create_gradient_panel(app):
    """Create the gradient squares panel."""
    app.squares_frame = tk.Frame(app.root)
    app.squares_frame.pack(fill="x")
    app.squares = []
    app.square_size = 24

def create_export_button(app):
    """Create export button."""
    app.export_btn = tk.Button(
        app.root, 
        text="Export Palette (.gpl)", 
        command=app.export_palette
    )
    app.export_btn.pack(pady=8)
