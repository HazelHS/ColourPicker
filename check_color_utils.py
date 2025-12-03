"""
Script to examine and verify the color_utils.py implementation.
"""

def analyze_color_dict():
    """Analyze the color dictionary structure."""
    from color_utils import init_color_dict, _colour_dict, get_colour_name, rgb_to_hex
    
    init_color_dict()
    
    print("Color Dictionary Analysis")
    print("=" * 70)
    print(f"Total colors in dictionary: {len(_colour_dict)}")
    print()
    
    # Sample some colors to check format
    print("Sample color entries:")
    print("-" * 70)
    for i, (name, rgb) in enumerate(list(_colour_dict.items())[:10]):
        hex_code = rgb_to_hex(rgb)
        # Verify the RGB values match the name
        lookup_name = get_colour_name(rgb)
        match = "✓" if lookup_name.lower() == name.lower() else "✗"
        print(f"{match} {name:20s} RGB{rgb} {hex_code} -> lookup: {lookup_name}")
    
    print()
    print("Checking specific colors:")
    print("-" * 70)
    
    # Check if silver is in the dictionary
    if "silver" in _colour_dict:
        rgb = _colour_dict["silver"]
        hex_code = rgb_to_hex(rgb)
        print(f"✓ 'silver' found: RGB{rgb} {hex_code}")
        
        # Verify reverse lookup
        lookup = get_colour_name(rgb)
        if lookup.lower() == "silver":
            print(f"  ✓ Reverse lookup successful: {lookup}")
        else:
            print(f"  ✗ Reverse lookup failed: got '{lookup}' instead of 'silver'")
    else:
        print("✗ 'silver' not found in dictionary!")
    
    print()
    
    # Test the distance calculation
    test_rgb = (192, 192, 192)  # silver
    name = get_colour_name(test_rgb)
    print(f"Distance test for RGB{test_rgb}:")
    print(f"  Result: {name}")


if __name__ == "__main__":
    analyze_color_dict()
