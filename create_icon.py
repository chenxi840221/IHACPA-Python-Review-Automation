#!/usr/bin/env python3
"""
Create a simple icon for the IHACPA application
This creates a basic icon with text that can be used for the executable
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a 256x256 image with a blue gradient background
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for y in range(size):
        color = int(50 + (y / size) * 100)  # Blue gradient
        draw.rectangle([(0, y), (size, y+1)], fill=(0, color, 200, 255))
    
    # Draw border
    border_width = 8
    draw.rectangle([(0, 0), (size-1, size-1)], outline=(0, 50, 150, 255), width=border_width)
    
    # Draw text
    try:
        # Try to use a nice font if available
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw "IHACPA" text
    text1 = "IHACPA"
    bbox1 = draw.textbbox((0, 0), text1, font=font_large)
    text1_width = bbox1[2] - bbox1[0]
    text1_height = bbox1[3] - bbox1[1]
    x1 = (size - text1_width) // 2
    y1 = size // 3 - text1_height // 2
    
    # Draw text with shadow
    draw.text((x1+3, y1+3), text1, font=font_large, fill=(0, 0, 0, 128))  # Shadow
    draw.text((x1, y1), text1, font=font_large, fill=(255, 255, 255, 255))  # Main text
    
    # Draw "Auto" text
    text2 = "Auto"
    bbox2 = draw.textbbox((0, 0), text2, font=font_small)
    text2_width = bbox2[2] - bbox2[0]
    text2_height = bbox2[3] - bbox2[1]
    x2 = (size - text2_width) // 2
    y2 = 2 * size // 3 - text2_height // 2
    
    draw.text((x2+2, y2+2), text2, font=font_small, fill=(0, 0, 0, 128))  # Shadow
    draw.text((x2, y2), text2, font=font_small, fill=(255, 255, 255, 255))  # Main text
    
    # Save as ICO file
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Icon created successfully: icon.ico")
    
    # Also save as PNG for reference
    img.save('icon.png')
    print("PNG version saved: icon.png")
    
except ImportError:
    print("Pillow library not installed. Creating a simple text file as placeholder.")
    print("To create a proper icon, install Pillow: pip install Pillow")
    
    # Create a placeholder
    with open('icon.ico', 'w') as f:
        f.write("IHACPA")
    print("Placeholder icon.ico created")

except Exception as e:
    print(f"Error creating icon: {e}")
    print("You can manually create an icon or use any ICO file named 'icon.ico'")