#!/usr/bin/env python3
"""
Generate external reader font .bin files for CrossPoint Reader.
Binary format: direct Unicode codepoint indexing (offset = codepoint * bytesPerChar)
Filename format: FontName_size_WxH.bin

Usage:
    python3 generate_reader_font_bin.py --font /path/to/font.ttf --size 32 --name NotoSansKR --output fonts/
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: PIL/Pillow not installed. Run: pip3 install Pillow")
    sys.exit(1)


# Maximum codepoint to include (covers Hangul syllables 0xAC00-0xD7A3)
MAX_CODEPOINT = 0xD7A3 + 1  # 55,204

# Unicode ranges to render (others will be zero-filled)
RENDER_RANGES = [
    (0x0020, 0x007E),   # Basic Latin (ASCII printable)
    (0x00A0, 0x00FF),   # Latin-1 Supplement
    (0x2000, 0x206F),   # General Punctuation
    (0x2E80, 0x2EFF),   # CJK Radicals Supplement
    (0x3000, 0x303F),   # CJK Symbols and Punctuation
    (0x3040, 0x309F),   # Hiragana
    (0x30A0, 0x30FF),   # Katakana
    (0x3100, 0x312F),   # Bopomofo
    (0x3130, 0x318F),   # Hangul Compatibility Jamo
    (0x31F0, 0x31FF),   # Katakana Phonetic Extensions
    (0x3200, 0x32FF),   # Enclosed CJK Letters
    (0x3400, 0x4DBF),   # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0xAC00, 0xD7A3),   # Hangul Syllables (11,172 chars)
    (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    (0xFE30, 0xFE4F),   # CJK Compatibility Forms
    (0xFF00, 0xFF60),   # Fullwidth Forms
    (0xFFF0, 0xFFFD),   # Specials
]


def should_render(codepoint):
    for start, end in RENDER_RANGES:
        if start <= codepoint <= end:
            return True
    return False


def generate_bin(font_path, pixel_size, font_name, output_dir):
    # Load font
    try:
        font = ImageFont.truetype(font_path, pixel_size)
    except Exception as e:
        print(f"Error loading font: {e}")
        return False

    ascent, descent = font.getmetrics()
    font_height = ascent + descent

    # Use pixel_size for both width and height (square cells for CJK)
    char_w = pixel_size
    char_h = pixel_size
    bytes_per_row = (char_w + 7) // 8
    bytes_per_char = bytes_per_row * char_h

    # Baseline positioning
    baseline = pixel_size - descent

    output_filename = f"{font_name}_{pixel_size}_{char_w}x{char_h}.bin"
    output_path = Path(output_dir) / output_filename
    total_size = MAX_CODEPOINT * bytes_per_char

    print(f"Generating: {output_filename}")
    print(f"  Font: {font_path}")
    print(f"  Size: {pixel_size}px ({char_w}x{char_h})")
    print(f"  Bytes per char: {bytes_per_char}")
    print(f"  Max codepoint: U+{MAX_CODEPOINT-1:04X}")
    print(f"  Total file size: {total_size / 1024 / 1024:.1f} MB")

    rendered = 0
    empty_block = b'\x00' * bytes_per_char

    with open(output_path, 'wb') as f:
        for cp in range(MAX_CODEPOINT):
            if not should_render(cp):
                f.write(empty_block)
                continue

            char = chr(cp)

            # Create bitmap
            img = Image.new('1', (char_w, char_h), 0)
            draw = ImageDraw.Draw(img)

            try:
                draw.text((0, baseline), char, font=font, fill=1, anchor="ls")
            except TypeError:
                draw.text((0, baseline - ascent), char, font=font, fill=1)

            # Convert to bytes
            bitmap_bytes = bytearray(bytes_per_char)
            for row in range(char_h):
                for byte_idx in range(bytes_per_row):
                    byte_val = 0
                    for bit in range(8):
                        px = byte_idx * 8 + bit
                        if px < char_w:
                            if img.getpixel((px, row)):
                                byte_val |= (1 << (7 - bit))
                    bitmap_bytes[row * bytes_per_row + byte_idx] = byte_val

            f.write(bitmap_bytes)
            rendered += 1

            if rendered % 1000 == 0:
                print(f"  Rendered {rendered} glyphs...")

    print(f"  Done: {rendered} glyphs rendered")
    print(f"  Output: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate CrossPoint reader font .bin')
    parser.add_argument('--font', type=str, required=True, help='Path to TTF/OTF font file')
    parser.add_argument('--size', type=int, default=32, help='Font size in pixels (default: 32)')
    parser.add_argument('--name', type=str, required=True, help='Font name for output filename')
    parser.add_argument('--output', type=str, default='fonts/', help='Output directory (default: fonts/)')
    args = parser.parse_args()

    if not Path(args.font).exists():
        print(f"Error: Font file not found: {args.font}")
        sys.exit(1)

    Path(args.output).mkdir(parents=True, exist_ok=True)

    if generate_bin(args.font, args.size, args.name, args.output):
        print("Success!")
    else:
        print("Failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
