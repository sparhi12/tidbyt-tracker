"""
Tidbyt Flight Tracker Display
Resolution: 64x32
Left Half (32x32): 5 rows of flight information (Flush left, no clipping)
  Row 1 (Static): Flight Number (Gold)
  Row 2 (Static): Direction & Distance (Green)
  Row 3 (Static): Route Codes (Amber)
  Row 4 (Scrolling): Airline Name (Sky Blue)
  Row 5 (Scrolling): Route Cities (Soft White)
Right Half (32x32): Real-time analog clock
"""

load("encoding/base64.star", "base64")
load("render.star", "render")

def main(config):
    flight_no = config.get("flight_no", "SCANNING").strip()
    airline = config.get("airline", "Seattle Skies").strip()
    row3_text = config.get("row3_text", "Nw 0.00").strip()
    route_codes = config.get("route_codes", "SEA>---").strip()
    route_cities = config.get("route_cities", "Seattle > Clear Sky").strip()
    clock_b64 = config.get("clock_b64", "")

    # Left Column: exactly 32px wide x 32px high, containing 5 rows (6px each)
    # Rows 2 & 3 are anchored flush to the left edge (x=0) without left padding.
    left_column = render.Column(
        expanded = True,
        main_align = "space_between",
        cross_align = "start",
        children = [
            # Row 1: Flight Number (Static, Centered, Gold)
            render.Box(
                width = 32,
                height = 6,
                child = render.Text(
                    content = flight_no,
                    font = "tom-thumb",
                    color = "#FFD700",
                ),
            ),
            # Row 2: Direction & Distance (Static, Green, e.g. "Nw 0.12", flush left)
            render.Text(
                content = row3_text,
                font = "tom-thumb",
                color = "#4ADE80",
            ),
            # Row 3: Route Codes (Static, Amber, e.g. "SEA>SFO", flush left)
            render.Text(
                content = route_codes,
                font = "tom-thumb",
                color = "#FB923C",
            ),
            # Row 4: Airline Name (Marquee fast scroll, Sky Blue)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    delay = 0,
                    child = render.Text(
                        content = airline,
                        font = "tom-thumb",
                        color = "#38BDF8",
                    ),
                ),
            ),
            # Row 5: Origin > Destination Full City Names (Marquee fast scroll, Soft White)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    delay = 0,
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
