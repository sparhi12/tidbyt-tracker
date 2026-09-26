"""
Analog clock image generator for Tidbyt (32x32 pixels).
Draws bezel, hour ticks, hour hand, minute hand, and second hand,
and outputs a base64-encoded PNG image for Starlark consumption.
"""

import base64
from datetime import datetime
import io
import math
from typing import Optional
from PIL import Image, ImageDraw

def generate_analog_clock(dt: Optional[datetime] = None) -> str:
    """
    Generate a 32x32 PNG of an analog clock at the given datetime.
    Returns: base64-encoded PNG string.
    """
    if dt is None:
        dt = datetime.now()

    # Create 32x32 transparent canvas
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center_x = 15.5
    center_y = 15.5
    radius = 14.5

    # 1. Bezel rim and dial face
    # Circle bounds: [1, 1, 30, 30]
    draw.ellipse([1, 1, 30, 30], outline=(71, 85, 105, 255), fill=(15, 23, 42, 255))

    # 2. Hour tick marks
    for h in range(12):
        angle_deg = h * 30.0 - 90.0
        angle_rad = math.radians(angle_deg)
        if h % 3 == 0:
            # Cardinal ticks (12, 3, 6, 9): 3px long, bright
            r_inner = radius - 3.5
            r_outer = radius - 1.0
            color = (226, 232, 240, 255)
            w = 1
        else:
            # Intermediate ticks: 1.5px long, subtle
            r_inner = radius - 2.0
            r_outer = radius - 1.0
            color = (100, 116, 139, 200)
            w = 1

        x1 = center_x + r_inner * math.cos(angle_rad)
        y1 = center_y + r_inner * math.sin(angle_rad)
        x2 = center_x + r_outer * math.cos(angle_rad)
        y2 = center_y + r_outer * math.sin(angle_rad)
        draw.line([(round(x1), round(y1)), (round(x2), round(y2))], fill=color, width=w)

    # 3. Hour Hand: 6.5 px long, 2px wide, white
    hour_val = (dt.hour % 12) + (dt.minute / 60.0) + (dt.second / 3600.0)
    hour_rad = math.radians(hour_val * 30.0 - 90.0)
    hx = center_x + 6.5 * math.cos(hour_rad)
    hy = center_y + 6.5 * math.sin(hour_rad)
    draw.line([(round(center_x), round(center_y)), (round(hx), round(hy))], fill=(255, 255, 255, 255), width=2)

    # 4. Minute Hand: 10.5 px long, 1px wide, sky blue
    min_val = dt.minute + (dt.second / 60.0)
    min_rad = math.radians(min_val * 6.0 - 90.0)
    mx = center_x + 10.5 * math.cos(min_rad)
    my = center_y + 10.5 * math.sin(min_rad)
    draw.line([(round(center_x), round(center_y)), (round(mx), round(my))], fill=(56, 189, 248, 255), width=1)

    # 5. Second Hand: 11.5 px long, 1px wide, crimson red
    sec_val = dt.second
    sec_rad = math.radians(sec_val * 6.0 - 90.0)
    sx = center_x + 11.5 * math.cos(sec_rad)
    sy = center_y + 11.5 * math.sin(sec_rad)
    # Slight counter-balance tail (2.5px backward)
    tx = center_x - 2.5 * math.cos(sec_rad)
    ty = center_y - 2.5 * math.sin(sec_rad)
    draw.line([(round(tx), round(ty)), (round(sx), round(sy))], fill=(239, 68, 68, 255), width=1)

    # 6. Center hub dot
    draw.ellipse([round(center_x - 1), round(center_y - 1), round(center_x + 1), round(center_y + 1)], fill=(239, 68, 68, 255))

    # Convert to base64 PNG
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
