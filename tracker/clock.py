"""
Analog clock image generator for Tidbyt (32x32 pixels).
Renders a pixel-perfect circular dial using Euclidean distance rasterization,
prominent cardinal hour ticks (12, 3, 6, 9), subtle single-pixel minor ticks,
and crisp hour/minute hands (with optional second hand).
"""

import base64
from datetime import datetime
import io
import math
from typing import Optional
from PIL import Image, ImageDraw

def generate_analog_clock(dt: Optional[datetime] = None, show_second_hand: bool = False) -> str:
    """
    Generate a 32x32 PNG of an analog clock at the given datetime.
    Returns: base64-encoded PNG string.
    """
    if dt is None:
        dt = datetime.now()

    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    pixels = img.load()

    center_x = 15.5
    center_y = 15.5
    outer_radius = 14.5
    inner_radius = 13.5

    # 1. Pixel-perfect Euclidean circular bezel and dial face
    # Completely avoids PIL ellipse flattening at top/bottom/left/right
    for y in range(32):
        for x in range(32):
            dx = x - center_x
            dy = y - center_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= inner_radius:
                # Dark navy dial interior
                pixels[x, y] = (15, 23, 42, 255)
            elif dist <= outer_radius:
                # Slate bezel ring
                pixels[x, y] = (71, 85, 105, 255)
            elif dist <= outer_radius + 0.5:
                # Subtle antialiased edge
                alpha = int(255 * (1.0 - (dist - outer_radius) / 0.5))
                pixels[x, y] = (51, 65, 85, alpha)

    draw = ImageDraw.Draw(img)

    # 2. Hour tick marks
    # Cardinal ticks (12, 3, 6, 9): prominent 2.5px white lines
    # Non-cardinal ticks (1, 2, 4, 5, 7, 8, 10, 11): subtle 1-pixel dots
    for h in range(12):
        angle_deg = h * 30.0 - 90.0
        angle_rad = math.radians(angle_deg)

        if h % 3 == 0:
            # Main cardinal marks: 2.5px long, bright white
            r1 = inner_radius - 3.0
            r2 = inner_radius - 1.0
            x1 = center_x + r1 * math.cos(angle_rad)
            y1 = center_y + r1 * math.sin(angle_rad)
            x2 = center_x + r2 * math.cos(angle_rad)
            y2 = center_y + r2 * math.sin(angle_rad)
            draw.line([(round(x1), round(y1)), (round(x2), round(y2))], fill=(248, 250, 252, 255), width=1)
        else:
            # Minor marks: small 1-pixel dot placed 1.5px inside rim
            r_dot = inner_radius - 1.8
            dx = round(center_x + r_dot * math.cos(angle_rad))
            dy = round(center_y + r_dot * math.sin(angle_rad))
            if 0 <= dx < 32 and 0 <= dy < 32:
                pixels[dx, dy] = (100, 116, 139, 210)

    # 3. Hour Hand: length 6.0 px, width 2px, vibrant red
    hour_val = (dt.hour % 12) + (dt.minute / 60.0)
    hour_rad = math.radians(hour_val * 30.0 - 90.0)
    hx = center_x + 6.0 * math.cos(hour_rad)
    hy = center_y + 6.0 * math.sin(hour_rad)
    draw.line([(round(center_x), round(center_y)), (round(hx), round(hy))], fill=(239, 68, 68, 255), width=2)

    # 4. Minute Hand: length 10.0 px, width 1px, vibrant sky blue
    min_val = dt.minute + (dt.second / 60.0)
    min_rad = math.radians(min_val * 6.0 - 90.0)
    mx = center_x + 10.0 * math.cos(min_rad)
    my = center_y + 10.0 * math.sin(min_rad)
    draw.line([(round(center_x), round(center_y)), (round(mx), round(my))], fill=(56, 189, 248, 255), width=1)

    # 5. Optional Second Hand
    if show_second_hand:
        sec_val = dt.second
        sec_rad = math.radians(sec_val * 6.0 - 90.0)
        sx = center_x + 11.0 * math.cos(sec_rad)
        sy = center_y + 11.0 * math.sin(sec_rad)
        tx = center_x - 2.0 * math.cos(sec_rad)
        ty = center_y - 2.0 * math.sin(sec_rad)
        draw.line([(round(tx), round(ty)), (round(sx), round(sy))], fill=(239, 68, 68, 255), width=1)
        center_color = (239, 68, 68, 255)
    else:
        center_color = (255, 255, 255, 255)

    # 6. Center hub dot
    cx = round(center_x)
    cy = round(center_y)
    pixels[cx, cy] = center_color
    pixels[cx - 1, cy] = center_color
    pixels[cx, cy - 1] = center_color
    pixels[cx - 1, cy - 1] = center_color

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
