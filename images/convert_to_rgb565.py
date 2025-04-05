# Call with python3 convert_to_rgb565.py <input_image_path>
# Example: python3 convert_to_rgb565.py path/to/logo.png
# Output in the same directory as the input file: logo.bin

import argparse
import os.path
from PIL import Image
import struct

"""
Converts an image to a binary format suitable for display on an ST7735 TFT display
using MicroPython on an ESP32. The output file includes a header with the image
dimensions followed by pixel data in RGB565 format.

Output File Format (e.g., logo.bin):
- Bytes 0-1: Width of the image (16-bit unsigned integer, big-endian)
- Bytes 2-3: Height of the image (16-bit unsigned integer, big-endian)
- Bytes 4+: Pixel data in RGB565 format (2 bytes per pixel, big-endian)
  - RGB565 format: 16 bits per pixel, with 5 bits for red, 6 bits for green, 5 bits for blue
  - Bit layout: RRRRRGGG GGGBBBBB
  - For an image of width W and height H, the total file size is 4 + (W * H * 2) bytes

Example:
- For a 25x6 image:
  - Header: 4 bytes (width=25, height=6)
  - Pixel data: 25 * 6 * 2 = 300 bytes
  - Total file size: 4 + 300 = 304 bytes
"""

# Set up argument parser
parser = argparse.ArgumentParser(description="Convert an image to RGB565 binary format for ST7735 display.")
parser.add_argument("input_path", help="Path to the input image file (e.g., logo.png)")
args = parser.parse_args()

# Get the input path and derive the output path
input_path = args.input_path
# Get the directory and base name of the input file
input_dir = os.path.dirname(input_path)
input_basename = os.path.splitext(os.path.basename(input_path))[0]
# Construct the output path: same directory, same base name, .bin extension
output_path = os.path.join(input_dir, f"{input_basename}.bin")

# Open the image
img = Image.open(input_path).convert("RGB")
width, height = img.size

# Open a binary file to write the RGB565 data with a header
with open(output_path, "wb") as f:
    # Write the header: width and height as 16-bit unsigned integers (big-endian)
    f.write(struct.pack(">H", width))  # Width (2 bytes)
    f.write(struct.pack(">H", height))  # Height (2 bytes)

    # Convert and write the pixel data as RGB565
    for y in range(height):
        for x in range(width):
            # Get the RGB values of the pixel
            r, g, b = img.getpixel((x, y))
            # Convert to RGB565
            # R (5 bits): Take the 5 most significant bits of red
            # G (6 bits): Take the 6 most significant bits of green
            # B (5 bits): Take the 5 most significant bits of blue
            r = (r >> 3) & 0x1F  # 5 bits
            g = (g >> 2) & 0x3F  # 6 bits
            b = (b >> 3) & 0x1F  # 5 bits
            # Combine into a 16-bit value: RRRRRGGG GGGBBBBB
            rgb565 = (r << 11) | (g << 5) | b
            # Write as two bytes (big-endian)
            f.write(struct.pack(">H", rgb565))  # 16-bit unsigned short

print(f"Converted image to RGB565 with header. Width: {width}, Height: {height}")
print(f"Output saved to: {output_path}")
