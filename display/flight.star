"""
Tidbyt Flight Tracker Display
Resolution: 64x32
Left Half: 5 rows of flight information (Row 3 static without scrolling)
Right Half: Real-time 32x32 analog clock
"""

load("encoding/base64.star", "base64")
load("render.star", "render")

def main(config):
    # Left Half Inputs
    flight_no = config.get("flight_no", "SCANNING")
    airline = config.get("airline", "Seattle Skies")
    # Row 3: e.g. "NW -> 0.1m" (Static, no marquee)
    row3_text = config.get("row3_text", "NW -> 0.1m")
    route_codes = config.get("route_codes", "SEA > ---")
    route_cities = config.get("route_cities", "Seattle > Clear Sky")

    # Right Half: Base64-encoded 32x32 PNG of the analog clock
    clock_b64 = config.get("clock_b64", "")

    # Left Column: 32px wide x 32px high, containing 5 rows (6px each, with slight padding)
    left_column = render.Column(
        expanded = True,
        main_align = "space_between",
        cross_align = "start",
        children = [
            # Row 1: Flight Number
            render.Box(
                width = 32,
                height = 6,
                child = render.Text(
                    content = flight_no,
                    font = "tom-thumb",
                    color = "#FFD700",
                ),
            ),
            # Row 2: Airline Name (Marquee for long names)
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
            # Row 3: Compass direction + distance (e.g. "NW -> 0.1m", strictly static without scrolling)
            render.Box(
                width = 32,
                height = 6,
                child = render.Text(
                    content = row3_text,
                    font = "tom-thumb",
                    color = "#4ADE80",
                ),
            ),
            # Row 4: Origin > Destination Codes (Marquee)
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
            # Row 5: Origin > Destination Full City Names (Marquee)
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
