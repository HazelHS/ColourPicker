"""
Color Wheel Picker - Main Application
A modular color picker with HSV wheel, gradient generation, and palette export.
"""
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk
import math
import colorsys
import tkinter.filedialog as fd
import os
from export_palette import export_palette

# Import our modules
from color_utils import (
    init_color_dict, 
    hsv_to_rgb255, 
    rgb_to_hex, 
    rgb_to_hsv,
    hex_to_rgb,
    get_colour_name,
    calculate_opposite_hue,
    get_color_info
)
from wheel_generator import generate_colour_wheel
from ui_components import (
    SliderWithEntry,
    ColorInputPanel,
    create_color_input_panel,
    create_main_sliders,
    create_fine_tune_panel,
    create_color_wheel,
    create_text_display,
    create_gradient_panel,
    create_export_button,
)
from gradient_logic import GradientCalculator, curve_t, calculate_gradient_colors, get_gradient_color_at_index


class ColourWheelApp:
    """Main application for the color wheel picker."""
    
    def __init__(self, root):
        """
        Initialize the color wheel picker application.
        
        Args:
            root: The tkinter root window
        """
        init_color_dict()
        self.size = 300
        self.root = root
        self.root.title("Colour Wheel Picker")
        
        # Main state variables
        self.hue_shift = 0.0
        self.shade = 1.0
        self.locked = False
        self.last_event = None
        self.last_panel = "wheel"
        self.last_square_idx = None
        self.hovered_square_idx = None
        
        # Selected color state
        self.selected_h = None
        self.selected_s = None
        self.selected_v = None
        self.selected_rgb = None
        self.selected_opp_h = None
        self.selected_opp_rgb = None
        
        # Gradient parameters
        self.gradient_steps = 20
        self.gradient_curve = 0
        self.fine_shade1 = 1.0
        self.fine_shade2 = 1.0
        self.fine_hue2 = 0.0
        
        # Gradient calculator
        self.gradient_calc = GradientCalculator()
        
        # Debounce timer for populate_squares
        self.populate_timer = None
        
        # Build UI using delegated functions
        create_color_input_panel(self)
        create_main_sliders(self, 400)
        create_fine_tune_panel(self)
        create_color_wheel(self)
        create_text_display(self)
        create_gradient_panel(self)
        # Place the gradient hover text box directly below the gradient squares
        self.square_hover_text = tk.Text(self.root, height=1, font=("Arial", 12), wrap="none")
        self.square_hover_text.pack(after=self.squares_frame, fill="x")
        self.square_hover_text.config(state="disabled")
        create_export_button(self)
        # Initialize display
        self.populate_squares()
    
    def _get_default_colors(self):
        """Get default start and end colors for gradient."""
        if self.selected_h is not None and self.selected_s is not None and self.selected_v is not None:
            h1, s1, v1 = self.selected_h, self.selected_s, self.selected_v
            h2, s2, v2 = self.selected_opp_h, self.selected_s, self.selected_v
        else:
            h1 = (0 + self.hue_shift) % 1.0
            s1 = 1
            v1 = self.shade
            h2 = (h1 + 0.5) % 1.0
            s2 = 1
            v2 = self.shade
        return h1, s1, v1, h2, s2, v2
    
    def _update_color_display(self, color_info):
        """Update text display and input fields with color info."""
        text = (
            f"Colour: {color_info['hex']} {color_info['rgb']} {color_info['name']}\n"
            f"Opposite: {color_info['opp_hex']} {color_info['opp_rgb']} {color_info['opp_name']}"
        )
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state="disabled")
        
        self.color_input.set_rgb(*color_info['rgb'])
        self.color_input.set_hex(color_info['hex'])
    
    def _update_gradient_endpoints_display(self):
        """Update text display to show first and last gradient colors (what will be exported)."""
        steps = int(self.gradient_steps)
        h1, s1, v1, h2, s2, v2 = self._get_default_colors()
        
        # Get first color (index 0)
        first_color_info = get_gradient_color_at_index(
            0, steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.gradient_curve, self.shade
        )
        
        # Get last color (index steps-1)
        last_color_info = get_gradient_color_at_index(
            steps - 1, steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.gradient_curve, self.shade
        )
        
        # Display first and last colors
        text = (
            f"Start: {first_color_info['hex']} {first_color_info['rgb']} {first_color_info['name']}\n"
            f"End: {last_color_info['hex']} {last_color_info['rgb']} {last_color_info['name']}"
        )
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state="disabled")
        
        # Update RGB/Hex inputs with first color
        self.color_input.set_rgb(*first_color_info['rgb'])
        self.color_input.set_hex(first_color_info['hex'])
    
    # Slider callbacks
    
    def on_slider(self, event=None):
        """Handle hue and shade slider changes."""
        old_hue = self.hue_shift
        self.hue_shift = self.hue_slider_widget.get() / 360.0
        new_shade = self.shade_slider_widget.get() / 100.0
        
        # Update shade
        self.shade = new_shade
        
        # If we have a selected color, update it with the new hue shift
        if self.selected_h is not None:
            # Calculate the hue change
            hue_delta = self.hue_shift - old_hue
            
            # Apply hue change to selected color
            self.selected_h = (self.selected_h + hue_delta) % 1.0
            self.selected_opp_h = (self.selected_opp_h + hue_delta) % 1.0
            
            # Update selected color with new shade
            self.selected_v = self.shade
            
            # Get updated color info
            color_info = get_color_info(self.selected_h, self.selected_s, self.selected_v)
            self.selected_rgb = color_info['rgb']
            self.selected_opp_rgb = color_info['opp_rgb']
            
            # Update display
            self._update_color_display(color_info)
        
        # Update wheel
        self.img = generate_colour_wheel(self.size, self.hue_shift, self.shade)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)
        
        # Update displays
        self.schedule_populate_squares()
        if self.last_event and self.last_panel == "wheel":
            self.on_mouse_move(self.last_event)
        elif self.last_square_idx is not None and self.last_panel == "squares":
            self.on_square_hover(self.last_square_idx)
    
    def on_interval_slider(self, event=None):
        """Handle gradient steps slider change."""
        self.gradient_steps = int(self.interval_slider_widget.get())
        self.schedule_populate_squares()
        self._update_gradient_text_readout()

    def on_curve_slider(self, event=None):
        """Handle gradient curve slider change."""
        self.gradient_curve = self.curve_slider_widget.get()
        self.schedule_populate_squares()
        self._update_gradient_text_readout()

    def on_fine_slider(self, event=None):
        """Handle fine-tune slider changes."""
        self.fine_shade1 = self.fine_shade1_widget.get() / 100.0
        self.fine_shade2 = self.fine_shade2_widget.get() / 100.0
        self.fine_hue2 = self.fine_hue2_widget.get() / 360.0
        self.schedule_populate_squares()
        
        # Always update the gradient endpoints display when fine-tune sliders change
        self._update_gradient_endpoints_display()

    def _update_gradient_text_readout(self):
        """Update text display to match the hovered/locked gradient square."""
        # Only update if we're actively in squares mode
        if self.last_panel != "squares" or self.last_square_idx is None:
            return
        
        steps = int(self.gradient_steps)
        idx = self.last_square_idx
        
        h1, s1, v1, h2, s2, v2 = self._get_default_colors()
        
        # Get color info for this index
        color_info = get_gradient_color_at_index(
            idx, steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.gradient_curve, self.shade
        )
        
        # Show the specific square's color instead of gradient endpoints
        self._update_color_display(color_info)

    def schedule_populate_squares(self):
        """Debounce populate_squares calls - only execute after 50ms of inactivity."""
        if self.populate_timer:
            self.root.after_cancel(self.populate_timer)
        self.populate_timer = self.root.after(50, self.populate_squares)
    
    # Color input callbacks
    
    def apply_rgb_input(self):
        """Apply color from RGB input fields."""
        rgb = self.color_input.get_rgb()
        if rgb:
            self.set_color_from_rgb(*rgb)
    
    def apply_hex_input(self):
        """Apply color from Hex input field."""
        hex_str = self.color_input.get_hex()
        rgb = hex_to_rgb(hex_str)
        if rgb:
            self.set_color_from_rgb(*rgb)
    
    def set_color_from_rgb(self, r, g, b):
        """
        Set the selected color from RGB values.
        
        Args:
            r, g, b: RGB values (0-255)
        """
        # Convert RGB to HSV
        h, s, v = rgb_to_hsv(r, g, b)
        
        # Store selected color info
        self.selected_h = h
        self.selected_s = s
        self.selected_v = v
        self.selected_opp_h = calculate_opposite_hue(h)
        
        # Get color info
        color_info = get_color_info(h, s, v)
        self.selected_rgb = color_info['rgb']
        self.selected_opp_rgb = color_info['opp_rgb']
        
        # Update display
        self._update_color_display(color_info)
        
        # Update gradient squares
        self.schedule_populate_squares()
        
        # Lock to this color
        self.locked = True
        self.last_panel = "wheel"
    
    # Mouse event handlers
    
    def on_mouse_move(self, event):
        """Handle mouse movement over color wheel."""
        self.last_event = event
        self.hovered_square_idx = None
        
        if self.locked and (self.last_panel == "squares" or self.last_panel == "wheel"):
            return
        
        x, y = event.x, event.y
        center = self.size // 2
        dx = x - center
        dy = y - center
        r = math.sqrt(dx*dx + dy*dy)
        radius = self.size // 2 - 2
        
        if 0 <= x < self.size and 0 <= y < self.size and r <= radius:
            # Calculate color at mouse position
            angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            shifted_angle = (angle + self.hue_shift) % 1.0
            s = r / radius
            v = self.shade
            
            # Get color info
            color_info = get_color_info(shifted_angle, s, v)
            
            # Update display
            self._update_color_display(color_info)
            
            # Clear square_hover_text when hovering wheel
            self.square_hover_text.config(state="normal")
            self.square_hover_text.delete("1.0", tk.END)
            self.square_hover_text.config(state="disabled")
            
            self.last_panel = "wheel"
            self.last_square_idx = None
            
            # Store for gradient
            self.selected_h = shifted_angle
            self.selected_s = s
            self.selected_v = v
            self.selected_rgb = color_info['rgb']
            self.selected_opp_h = color_info['opp_h']
            self.selected_opp_rgb = color_info['opp_rgb']
            
            self.schedule_populate_squares()
        else:
            # Clear square_hover_text when mouse leaves wheel
            self.square_hover_text.config(state="normal")
            self.square_hover_text.delete("1.0", tk.END)
            self.square_hover_text.config(state="disabled")
    
    def toggle_lock(self, event):
        """Toggle lock state when clicking on wheel or squares."""
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
    
    # Gradient generation
    
    def curve_t(self, t, curve):
        """Delegate to gradient_logic.curve_t."""
        return curve_t(t, curve)

    def populate_squares(self):
        """Generate and display gradient color squares."""
        # Remove old squares
        for widget in self.squares_frame.winfo_children():
            widget.destroy()
        self.squares = []
        steps = int(self.gradient_steps)
        
        h1, s1, v1, h2, s2, v2 = self._get_default_colors()
        
        # Use the calculate_gradient_colors function
        colors = calculate_gradient_colors(
            steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.gradient_curve, self.shade
        )
        
        for i, rgb in enumerate(colors):
            hex_code = rgb_to_hex(rgb)
            square = tk.Label(
                self.squares_frame,
                bg=hex_code,
                width=2,
                height=1,
                relief="raised",
                borderwidth=2
            )
            square.grid(row=0, column=i, padx=1, pady=2)
            square.bind("<Enter>", lambda e, idx=i: self.on_square_hover(idx))
            square.bind("<Button-1>", lambda e, idx=i: self.on_square_click(idx))
            self.squares.append(square)

        # Update main text readout with gradient endpoints
        self._update_gradient_endpoints_display()

    def on_square_hover(self, idx):
        """Handle mouse hover over gradient square."""
        self.hovered_square_idx = idx
        steps = int(self.gradient_steps)
        
        h1, s1, v1, h2, s2, v2 = self._get_default_colors()
        
        # Get color info for this square
        color_info = get_gradient_color_at_index(
            idx, steps, h1, s1, v1, h2, s2, v2,
            self.fine_shade1, self.fine_shade2, self.fine_hue2,
            self.gradient_curve, self.shade
        )
        
        # Always show the single color in square_hover_text
        hover_text = f"{color_info['hex']} {color_info['rgb']} {color_info['name']}"
        self.square_hover_text.config(state="normal")
        self.square_hover_text.delete("1.0", tk.END)
        self.square_hover_text.insert(tk.END, hover_text)
        self.square_hover_text.config(state="disabled")
        
        # Only update the main display if not locked to wheel
        if not (self.locked and self.last_panel == "wheel"):
            self._update_color_display(color_info)
            self.last_panel = "squares"
            self.last_square_idx = idx

    def on_square_click(self, idx):
        """Handle clicking on a gradient square."""
        self.toggle_lock(None)
    
    # Export functionality
    
    def export_palette(self):
        """Export current gradient as a GIMP palette file (.gpl) using the export_palette module."""
        export_palette(
            self.gradient_steps,
            self.gradient_curve,
            self.fine_shade1,
            self.fine_shade2,
            self.fine_hue2,
            self.shade,
            self.hue_shift,
            self.selected_h,
            self.selected_s,
            self.selected_v,
            self.selected_opp_h,
        )


def main():
    """Application entry point."""
    root = tk.Tk()
    app = ColourWheelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
