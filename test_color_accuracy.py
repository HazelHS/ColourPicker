"""
Test script to verify color name accuracy against RGB and Hex values.
"""
import sys

try:
    from color_utils import init_color_dict, get_colour_name, rgb_to_hex, hex_to_rgb
except ImportError as e:
    print(f"Error importing color_utils: {e}")
    sys.exit(1)

def test_known_colors():
    """Test a set of known web colors to verify accuracy."""
    try:
        init_color_dict()
    except Exception as e:
        print(f"Error initializing color dictionary: {e}")
        print("This may indicate an issue with color_utils.py")
        return False
    
    # Known web colors with their exact RGB values
    test_colors = [
        ((255, 255, 255), "white", "#ffffff"),
        ((0, 0, 0), "black", "#000000"),
        ((255, 0, 0), "red", "#ff0000"),
        ((0, 255, 0), "lime", "#00ff00"),
        ((0, 0, 255), "blue", "#0000ff"),
        ((192, 192, 192), "silver", "#c0c0c0"),
        ((128, 128, 128), "gray", "#808080"),
        ((255, 255, 0), "yellow", "#ffff00"),
        ((255, 165, 0), "orange", "#ffa500"),
        ((128, 0, 128), "purple", "#800080"),
        ((0, 128, 128), "teal", "#008080"),
        ((255, 192, 203), "pink", "#ffc0cb"),
    ]
    
    print("Testing color name accuracy:")
    print("-" * 70)
    
    all_accurate = True
    for rgb, expected_name, expected_hex in test_colors:
        try:
            actual_name = get_colour_name(rgb)
            actual_hex = rgb_to_hex(rgb)
        except Exception as e:
            print(f"[X] RGB{rgb}")
            print(f"   ERROR: {type(e).__name__}: {e}")
            print()
            all_accurate = False
            continue
        
        name_match = actual_name.lower() == expected_name.lower()
        hex_match = actual_hex.lower() == expected_hex.lower()
        
        status = "[OK]" if name_match and hex_match else "[X]"
        if not (name_match and hex_match):
            all_accurate = False
        
        print(f"{status} RGB{rgb}")
        print(f"   Expected: {expected_name} ({expected_hex})")
        print(f"   Got:      {actual_name} ({actual_hex})")
        
        if not name_match:
            print(f"   WARNING: NAME MISMATCH")
        if not hex_match:
            print(f"   WARNING: HEX MISMATCH")
        print()
    
    print("-" * 70)
    if all_accurate:
        print("[OK] All colors accurate!")
    else:
        print("[X] Some color names are inaccurate")
    
    return all_accurate


def test_nearest_color():
    """Test the nearest color matching for non-exact colors."""
    try:
        init_color_dict()
    except Exception as e:
        print(f"Error initializing color dictionary: {e}")
        return
    
    print("\nTesting nearest color matching:")
    print("-" * 70)
    
    # Test colors that are close to known colors
    test_colors = [
        ((190, 190, 190), "Expected close to 'silver' (192,192,192)"),
        ((130, 130, 130), "Expected close to 'gray' (128,128,128)"),
        ((255, 160, 5), "Expected close to 'orange' (255,165,0)"),
    ]
    
    for rgb, description in test_colors:
        try:
            name = get_colour_name(rgb)
            hex_code = rgb_to_hex(rgb)
            print(f"RGB{rgb} -> {name} ({hex_code})")
            print(f"   {description}")
        except Exception as e:
            print(f"RGB{rgb} -> ERROR: {type(e).__name__}: {e}")
            print(f"   {description}")
        print()


if __name__ == "__main__":
    print("Checking color_utils.py implementation...")
    print()
    
    accurate = test_known_colors()
    test_nearest_color()
    
    if not accurate:
        print("\nRECOMMENDATION: Review color_utils.py to ensure:")
        print("   1. COLOR_CACHE is properly initialized (if used)")
        print("   2. Color dictionary has correct RGB values")
        print("   3. get_colour_name() uses proper distance calculation")
        print("   4. Hex conversion is accurate")
        print("\nThe error indicates COLOR_CACHE is undefined in color_utils.py")
        print("Please check line 187 in color_utils.py and initialize COLOR_CACHE")
