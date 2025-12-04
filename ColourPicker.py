"""
Color Wheel Picker - Main Application
A modular color picker with HSV wheel, gradient generation, and palette export.
"""
import tkinter as tk
import math
from PIL import ImageTk

# Import modules
from color_utils import (
    init_color_dict, 
    rgb_to_hsv,
    hex_to_rgb,
    calculate_opposite_hue,
    get_color_info
)
from wheel_generator import generate_colour_wheel
from ui_components import (
    create_color_input_panel,
    create_main_sliders,
    create_fine_tune_panel,
    create_color_wheel,
    create_text_display,
    create_gradient_panel,
    create_export_button,
)
from app_state import AppState
from gradient_display import GradientDisplay
from export_palette import export_palette


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
        
        # Application state
        self.state = AppState()
        self.last_event = None
        
        # Debounce timer
        self.populate_timer = None
        
        # Build UI
        create_color_input_panel(self)
        create_main_sliders(self, 400)
        create_fine_tune_panel(self)
        create_color_wheel(self)
        create_text_display(self)
        create_gradient_panel(self)
        
        # Initialize gradient display
        self.gradient_display = GradientDisplay(self.squares_frame, self.state)
        self.gradient_display.set_callbacks(self.on_square_hover, self.on_square_click)
        
        # Gradient hover text
        self.square_hover_text = tk.Text(self.root, height=1, font=("Arial", 12), wrap="none")
        self.square_hover_text.pack(after=self.squares_frame, fill="x")
        self.square_hover_text.config(state="disabled")
        
        create_export_button(self)
        
        # Initialize display
        self.populate_squares()
    
    # Properties for backward compatibility
    @property
    def hue_shift(self):
        return self.state.hue_shift
    
    @hue_shift.setter
    def hue_shift(self, value):
        self.state.hue_shift = value
    
    @property
    def shade(self):
        return self.state.shade
    
    @shade.setter
    def shade(self, value):
        self.state.shade = value
    
    @property
    def locked(self):
        return self.state.locked
    
    @locked.setter
    def locked(self, value):
        self.state.locked = value
    
    @property
    def gradient_steps(self):
        return self.state.gradient.steps
    
    @gradient_steps.setter
    def gradient_steps(self, value):
        self.state.gradient.steps = value
    
    @property
    def gradient_curve(self):
        return self.state.gradient.curve
    
    @gradient_curve.setter
    def gradient_curve(self, value):
        self.state.gradient.curve = value
    
    @property
    def fine_shade1(self):
        return self.state.gradient.fine_shade1
    
    @fine_shade1.setter
    def fine_shade1(self, value):
        self.state.gradient.fine_shade1 = value
    
    @property
    def fine_shade2(self):
        return self.state.gradient.fine_shade2
    
    @fine_shade2.setter
    def fine_shade2(self, value):
        self.state.gradient.fine_shade2 = value
    
    @property
    def fine_hue2(self):
        return self.state.gradient.fine_hue2
    
    @fine_hue2.setter
    def fine_hue2(self, value):
        self.state.gradient.fine_hue2 = value
    
    @property
    def color_depth(self):
        return self.state.color_depth

    @color_depth.setter
    def color_depth(self, value):
        self.state.color_depth = value

    @property
    def quantize_levels(self):
        return self.state.quantize_levels

    @quantize_levels.setter
    def quantize_levels(self, value):
        self.state.quantize_levels = int(value)

    # Display methods
    
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
        """Update text display to show first and last gradient colors."""
        first_color, last_color = self.gradient_display.get_gradient_endpoint_colors(
            self.state.hue_shift, self.state.shade, self.state.quantize_levels
        )
        
        text = (
            f"Start: {first_color['hex']} {first_color['rgb']} {first_color['name']}\n"
            f"End: {last_color['hex']} {last_color['rgb']} {last_color['name']}"
        )
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state="disabled")
        
        # Update inputs with first color
        self.color_input.set_rgb(*first_color['rgb'])
        self.color_input.set_hex(first_color['hex'])
    
    # Slider callbacks
    
    def on_depth_change(self):
        """Handle color depth selector change."""
        # depth_var set in ui_components.OptionMenu
        self.state.color_depth = getattr(self, "depth_var", tk.StringVar(value="unlimited")).get()
        # regenerate wheel with depth
        self.img = generate_colour_wheel(self.size, self.state.hue_shift, self.state.shade, self.state.quantize_levels)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)

        # update current color display using quantized color info
        color = self.state.color
        if color.h is not None:
            color_info = get_color_info(color.h, color.s, color.v, self.state.quantize_levels)
            color.rgb = color_info['rgb']
            color.opp_rgb = color_info['opp_rgb']
            self._update_color_display(color_info)

        # update gradient squares
        self.schedule_populate_squares()

    def on_quant_change(self):
        """Handle quantize slider change (slider + entry)."""
        # ignore changes when disabled
        if not getattr(self, "quant_enabled_var", tk.BooleanVar(value=True)).get():
            return

        # read float from the SliderWithEntry and convert to integer levels
        try:
            val = float(getattr(self, "quant_widget").get())
        except Exception:
            val = 256.0
        levels = int(round(val))
        # clamp to allowed range 1..256
        levels = max(1, min(256, levels))
        self.state.quantize_levels = levels

        # regenerate wheel with new levels
        self.img = generate_colour_wheel(self.size, self.state.hue_shift, self.state.shade, self.state.quantize_levels)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)

        # update current color display using quantized color info
        color = self.state.color
        if color.h is not None:
            color_info = get_color_info(color.h, color.s, color.v, self.state.quantize_levels)
            color.rgb = color_info['rgb']
            color.opp_rgb = color_info['opp_rgb']
            self._update_color_display(color_info)

        # update gradient squares
        self.schedule_populate_squares()

    def on_quant_toggle(self):
        """Enable or disable quantization feature from the checkbox."""
        enabled = getattr(self, "quant_enabled_var", tk.BooleanVar(value=True)).get()
        self.state.quantize_enabled = bool(enabled)

        # enable/disable the slider and entry widgets
        if hasattr(self, "quant_widget"):
            state = "normal" if enabled else "disabled"
            try:
                self.quant_widget.slider.config(state=state)
                self.quant_widget.entry.config(state=state)
            except Exception:
                pass

        # If disabled, set to full-range and update UI; if enabled, apply current slider value
        if not enabled:
            self.state.quantize_levels = 256
        else:
            # reapply slider value
            self.on_quant_change()

        # regenerate wheel and update displays regardless
        self.img = generate_colour_wheel(self.size, self.state.hue_shift, self.state.shade, self.state.quantize_levels)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)

        if self.state.color.h is not None:
            color_info = get_color_info(self.state.color.h, self.state.color.s, self.state.color.v, self.state.quantize_levels)
            self._update_color_display(color_info)

        self.schedule_populate_squares()

    def on_slider(self, event=None):
        """Handle hue and shade slider changes."""
        old_hue = self.state.hue_shift
        self.state.hue_shift = self.hue_slider_widget.get() / 360.0
        new_shade = self.shade_slider_widget.get() / 100.0
        self.state.shade = new_shade
        
        # Update selected color if exists
        color = self.state.color
        if color.h is not None:
            hue_delta = self.state.hue_shift - old_hue
            color.h = (color.h + hue_delta) % 1.0
            color.opp_h = (color.opp_h + hue_delta) % 1.0
            color.v = self.state.shade
            
            color_info = get_color_info(color.h, color.s, color.v, self.state.quantize_levels)
            color.rgb = color_info['rgb']
            color.opp_rgb = color_info['opp_rgb']
            
            self._update_color_display(color_info)
        
        # Update wheel (include depth)
        self.img = generate_colour_wheel(self.size, self.state.hue_shift, self.state.shade, self.state.quantize_levels)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_img)
        
        # Update displays
        self.schedule_populate_squares()
        if self.last_event and self.state.last_panel == "wheel":
            self.on_mouse_move(self.last_event)
        elif self.state.last_square_idx is not None and self.state.last_panel == "squares":
            self.on_square_hover(self.state.last_square_idx)
    
    def on_interval_slider(self, event=None):
        """Handle gradient steps slider change."""
        self.state.gradient.steps = int(self.interval_slider_widget.get())
        self.schedule_populate_squares()
        self._update_gradient_endpoints_display()

    def on_curve_slider(self, event=None):
        """Handle gradient curve slider change."""
        self.state.gradient.curve = self.curve_slider_widget.get()
        self.schedule_populate_squares()
        if self.state.last_panel == "squares" and self.state.last_square_idx is not None:
            self.on_square_hover(self.state.last_square_idx)

    def on_fine_slider(self, event=None):
        """Handle fine-tune slider changes."""
        gradient = self.state.gradient
        gradient.fine_shade1 = self.fine_shade1_widget.get() / 100.0
        gradient.fine_shade2 = self.fine_shade2_widget.get() / 100.0
        gradient.fine_hue2 = self.fine_hue2_widget.get() / 360.0
        self.schedule_populate_squares()
        self._update_gradient_endpoints_display()

    def schedule_populate_squares(self):
        """Debounce populate_squares calls."""
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
        """Set the selected color from RGB values."""
        h, s, v = rgb_to_hsv(r, g, b)
        
        color = self.state.color
        color.h = h
        color.s = s
        color.v = v
        color.opp_h = calculate_opposite_hue(h)
        
        color_info = get_color_info(h, s, v, self.state.quantize_levels)
        color.rgb = color_info['rgb']
        color.opp_rgb = color_info['opp_rgb']
        
        self._update_color_display(color_info)
        self.schedule_populate_squares()
        
        self.state.locked = True
        self.state.last_panel = "wheel"
    
    # Mouse event handlers
    
    def on_mouse_move(self, event):
        """Handle mouse movement over color wheel."""
        self.last_event = event
        self.state.hovered_square_idx = None
        
        if self.state.locked and (self.state.last_panel == "squares" or self.state.last_panel == "wheel"):
            return
        
        x, y = event.x, event.y
        center = self.size // 2
        dx = x - center
        dy = y - center
        r = math.sqrt(dx*dx + dy*dy)
        radius = self.size // 2 - 2
        
        if 0 <= x < self.size and 0 <= y < self.size and r <= radius:
            angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            shifted_angle = (angle + self.state.hue_shift) % 1.0
            s = r / radius
            v = self.state.shade
            
            color_info = get_color_info(shifted_angle, s, v, self.state.quantize_levels)
            self._update_color_display(color_info)
            
            # Clear square hover text
            self.square_hover_text.config(state="normal")
            self.square_hover_text.delete("1.0", tk.END)
            self.square_hover_text.config(state="disabled")
            
            self.state.last_panel = "wheel"
            self.state.last_square_idx = None
            
            # Update selected color
            color = self.state.color
            color.h = shifted_angle
            color.s = s
            color.v = v
            color.rgb = color_info['rgb']
            color.opp_h = color_info['opp_h']
            color.opp_rgb = color_info['opp_rgb']
            
            self.schedule_populate_squares()
        else:
            self.square_hover_text.config(state="normal")
            self.square_hover_text.delete("1.0", tk.END)
            self.square_hover_text.config(state="disabled")
    
    def toggle_lock(self, event):
        """Toggle lock state when clicking."""
        if self.state.hovered_square_idx is not None:
            self.state.locked = not self.state.locked
            if self.state.locked:
                self.state.last_panel = "squares"
                self.state.last_square_idx = self.state.hovered_square_idx
            else:
                self.state.last_panel = "wheel"
                self.state.last_square_idx = None
        else:
            self.state.locked = not self.state.locked
            if self.state.locked:
                self.state.last_panel = "wheel"
            else:
                self.state.last_panel = "wheel"
                self.state.last_square_idx = None
    
    # Gradient methods
    
    def populate_squares(self):
        """Generate and display gradient color squares."""
        self.gradient_display.populate(self.state.hue_shift, self.state.shade, self.state.quantize_levels)
        self._update_gradient_endpoints_display()

    def on_square_hover(self, idx):
        """Handle mouse hover over gradient square."""
        self.state.hovered_square_idx = idx
        
        color_info = self.gradient_display.get_color_at_index(
            idx, self.state.hue_shift, self.state.shade, self.state.quantize_levels
        )
        
        # Show in hover text
        hover_text = f"{color_info['hex']} {color_info['rgb']} {color_info['name']}"
        self.square_hover_text.config(state="normal")
        self.square_hover_text.delete("1.0", tk.END)
        self.square_hover_text.insert(tk.END, hover_text)
        self.square_hover_text.config(state="disabled")
        
        # Update main display if not locked to wheel
        if not (self.state.locked and self.state.last_panel == "wheel"):
            self._update_color_display(color_info)
            self.state.last_panel = "squares"
            self.state.last_square_idx = idx

    def on_square_click(self, idx):
        """Handle clicking on a gradient square."""
        self.toggle_lock(None)
    
    # Export
    
    def export_palette(self):
        """Export current gradient as GIMP palette."""
        export_palette(
            self.state.gradient.steps,
            self.state.gradient.curve,
            self.state.gradient.fine_shade1,
            self.state.gradient.fine_shade2,
            self.state.gradient.fine_hue2,
            self.state.shade,
            self.state.hue_shift,
            self.state.color.h,
            self.state.color.s,
            self.state.color.v,
            self.state.color.opp_h,
            self.state.quantize_levels
        )


def main():
    """Application entry point."""
    root = tk.Tk()
    app = ColourWheelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
