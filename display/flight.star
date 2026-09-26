"""
Tidbyt Flight Tracker Display
Resolution: 64x32
Left Half (32x32): 5 rows of flight information (Left-anchored, no clipping)
Right Half (32x32): Real-time analog clock
"""

load("encoding/base64.star", "base64")
load("render.star", "render")

def main(config):
    flight_no = config.get("flight_no", "SCANNING").strip()
    airline = config.get("airline", "Seattle Skies").strip()
    row3_text = config.get("row3_text", "NW -> 0.1m").strip()
    route_codes = config.get("route_codes", "SEA > ---").strip()
    route_cities = config.get("route_cities", "Seattle > Clear Sky").strip()
    clock_b64 = config.get("clock_b64", "")

    # Left Column: exactly 32px wide x 32px high, containing 5 rows (6px each)
    # Using cross_align = 'start' to ensure everything anchors flush to the left edge
    left_column = render.Column(
        expanded = True,
        main_align = "space_between",
        cross_align = "start",
        children = [
            # Row 1: Flight Number (Centered, gold)
            render.Box(
                width = 32,
                height = 6,
                child = render.Text(
                    content = flight_no,
                    font = "tom-thumb",
                    color = "#FFD700",
                ),
            ),
            # Row 2: Airline Name (Flush left, sky blue)
            # Fits statically for short names ("Alaska"), scrolls only if > 32px
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    child = render.Text(
                        content = airline,
                        font = "tom-thumb",
                        color = "#38BDF8",
                    ),
                ),
            ),
            # Row 3: Direction + Distance (e.g. "NW -> 0.1m", static, green, with 1px left padding to prevent edge cutting)
            render.Row(
                children = [
                    render.Padding(
                        pad = (1, 0, 0, 0),
                        child = render.Text(
                            content = row3_text,
                            font = "tom-thumb",
                            color = "#4ADE80",
                        ),
                    ),
                ],
            ),
            # Row 4: Origin > Destination Codes (Marquee, amber)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    child = render.Text(
                        content = route_codes,
                        font = "tom-thumb",
                        color = "#FB923C",
                    ),
                ),
            ),
            # Row 5: Origin > Destination Full City Names (Marquee, soft white)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    child = render.Text(
                        content = route_cities,
                        font = "tom-thumb",
                        color = "#E2E8F0",
                    ),
                ),
            ),
        ],
    )

    # Right side: 32x32 analog clock image
    right_clock = render.Box(
        width = 32,
        height = 32,
        child = render.Image(src = base64.decode(clock_b64)) if clock_b64 else render.Box(width = 32, height = 32),
    )

    return render.Root(
        child = render.Row(
            children = [
                render.Box(width = 32, height = 32, child = left_column),
                right_clock,
            ],
        ),
    )
