"""
Gradient display and interaction logic.
"""
import tkinter as tk
from color_utils import rgb_to_hex, get_colour_name
from gradient_logic import get_gradient_color_at_index, calculate_gradient_colors


class GradientDisplay:
    """Manages gradient square display and interactions."""
    
    def __init__(self, parent_frame, app_state):
        """
        Initialize gradient display.
        
        Args:
            parent_frame: Parent tkinter frame
            app_state: AppState instance
        """
        self.frame = parent_frame
        self.app_state = app_state
        self.squares = []
        self.square_size = 24
        self.on_hover_callback = None
        self.on_click_callback = None
    
    def set_callbacks(self, on_hover, on_click):
        """Set callbacks for square interactions."""
        self.on_hover_callback = on_hover
        self.on_click_callback = on_click
    
    def get_default_colors(self, hue_shift, shade):
        """Get default start and end colors for gradient."""
        color = self.app_state.color
        
        if color.h is not None and color.s is not None and color.v is not None:
            h1, s1, v1 = color.h, color.s, color.v
            h2, s2, v2 = color.opp_h, color.s, color.v
        else:
            h1 = (0 + hue_shift) % 1.0
            s1 = 1
            v1 = shade
            h2 = (h1 + 0.5) % 1.0
            s2 = 1
            v2 = shade
        
        return h1, s1, v1, h2, s2, v2
    
    def get_gradient_endpoint_colors(self, hue_shift, shade):
        """
        Get color info for first and last gradient colors.
        
        Returns:
            Tuple of (first_color_info, last_color_info)
        """
        gradient = self.app_state.gradient
        h1, s1, v1, h2, s2, v2 = self.get_default_colors(hue_shift, shade)
        
        first_color_info = get_gradient_color_at_index(
            0, gradient.steps, h1, s1, v1, h2, s2, v2,
            gradient.fine_shade1, gradient.fine_shade2, gradient.fine_hue2,
            gradient.curve, shade
        )
        
        last_color_info = get_gradient_color_at_index(
            gradient.steps - 1, gradient.steps, h1, s1, v1, h2, s2, v2,
            gradient.fine_shade1, gradient.fine_shade2, gradient.fine_hue2,
            gradient.curve, shade
        )
        
        return first_color_info, last_color_info
    
    def populate(self, hue_shift, shade):
        """Generate and display gradient color squares."""
        # Clear existing squares
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.squares = []
        
        gradient = self.app_state.gradient
        h1, s1, v1, h2, s2, v2 = self.get_default_colors(hue_shift, shade)
        
        # Generate colors
        colors = calculate_gradient_colors(
            gradient.steps, h1, s1, v1, h2, s2, v2,
            gradient.fine_shade1, gradient.fine_shade2, gradient.fine_hue2,
            gradient.curve, shade
        )
        
        # Create squares
        for i, rgb in enumerate(colors):
            hex_code = rgb_to_hex(rgb)
            square = tk.Label(
                self.frame,
                bg=hex_code,
                width=2,
                height=1,
                relief="raised",
                borderwidth=2
            )
            square.grid(row=0, column=i, padx=1, pady=2)
            
            if self.on_hover_callback:
                square.bind("<Enter>", lambda e, idx=i: self.on_hover_callback(idx))
            if self.on_click_callback:
                square.bind("<Button-1>", lambda e, idx=i: self.on_click_callback(idx))
            
            self.squares.append(square)
    
    def get_color_at_index(self, idx, hue_shift, shade):
        """Get color info for a specific gradient square."""
        gradient = self.app_state.gradient
        h1, s1, v1, h2, s2, v2 = self.get_default_colors(hue_shift, shade)
        
        return get_gradient_color_at_index(
            idx, gradient.steps, h1, s1, v1, h2, s2, v2,
            gradient.fine_shade1, gradient.fine_shade2, gradient.fine_hue2,
            gradient.curve, shade
        )
