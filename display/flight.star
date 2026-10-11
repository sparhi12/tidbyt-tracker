"""
Tidbyt Flight Tracker Display
Resolution: 64x32
Left Column: 5 rows of flight information (Flush left)
  Row 1 (Static): Flight Number
  Row 2 (Static): Direction & Distance
  Row 3 (Static): Route Codes (Separated with spaces, e.g. 'SEA > SFO', extending to clock edge)
  Row 4 (Scrolling): Airline Name (Extended to x=34 at clock bezel edge)
  Row 5 (Scrolling): Route Cities (Extended to x=38 at clock curve edge)
Right Side (32x32): Real-time analog clock
"""

load("encoding/base64.star", "base64")
load("render.star", "render")

def main(config):
    flight_no = config.get("flight_no", "SCANNING").strip()
    airline = config.get("airline", "Seattle Skies").strip()
    row3_text = config.get("row3_text", "Nw 0.00").strip()
    route_codes = config.get("route_codes", "SEA > ---").strip()
    route_cities = config.get("route_cities", "Seattle > Clear Sky").strip()
    clock_b64 = config.get("clock_b64", "")

    # Ensure route codes have spaces around '>' (e.g. 'SEA > SFO') to fill space before clock edge
    if ">" in route_codes and " > " not in route_codes:
        route_codes = route_codes.replace(">", " > ")

    # Compute adaptive scroll speed based on BOTH the polling interval and the fragment length.
    # In tom-thumb font, glyph width + inter-glyph spacing is ~4 pixels per character.
    max_len = max(len(airline), len(route_cities))
    text_px = max_len * 4

    # Distance to scroll so that even long fragments (e.g. "San Francisco > Portland")
    # show completely in one run:
    scroll_dist = max(25, text_px - 10)

    poll_interval_ms = int(config.get("poll_interval_ms", "1000"))
    frame_delay = max(12, min(80, poll_interval_ms // scroll_dist))

    # Pleasing, cohesive color palette (rotates on 8-hour day/sunset/night schedule)
    color_row1 = config.get("color_row1", "#38BDF8").strip()
    color_row2 = config.get("color_row2", "#2DD4BF").strip()
    color_row3 = config.get("color_row3", "#22D3EE").strip()
    color_row4 = config.get("color_row4", "#7DD3FC").strip()
    color_row5 = config.get("color_row5", "#E2E8F0").strip()

    # Left Column: containing 5 rows (6px each)
    # Rows 1, 2 & 3 are anchored flush to the left edge (x=0)
    # Rows 4 & 5 extend their scrolling window right to the curve of the clock bezel (x=34 and x=38)
    left_column = render.Column(
        expanded = True,
        main_align = "space_between",
        cross_align = "start",
        children = [
            # Row 1: Flight Number (Static, Flush Left)
            render.Text(
                content = flight_no,
                font = "tom-thumb",
                color = color_row1,
            ),
            # Row 2: Direction & Distance (Static, e.g. "Nw 0.12", Flush Left)
            render.Text(
                content = row3_text,
                font = "tom-thumb",
                color = color_row2,
            ),
            # Row 3: Route Codes (Static, e.g. "SEA > SFO", Flush Left, extends to clock edge)
            render.Text(
                content = route_codes,
                font = "tom-thumb",
                color = color_row3,
            ),
            # Row 4: Airline Name (Marquee scroll, boundary extended to clock bezel at x=34)
            render.Box(
                width = 34,
                height = 6,
                child = render.Marquee(
                    width = 34,
                    delay = 0,
                    child = render.Text(
                        content = airline,
                        font = "tom-thumb",
                        color = color_row4,
                    ),
                ),
            ),
            # Row 5: Origin > Destination Full City Names (Marquee scroll, boundary extended to clock curve at x=38)
            render.Box(
                width = 38,
                height = 6,
                child = render.Marquee(
                    width = 38,
                    delay = 0,
                    child = render.Text(
                        content = route_cities,
                        font = "tom-thumb",
                        color = color_row5,
                    ),
                ),
            ),
        ],
    )

    # Right side: 32x32 analog clock image positioned at x=32
    right_clock = render.Box(
        width = 32,
        height = 32,
        child = render.Image(src = base64.decode(clock_b64)) if clock_b64 else render.Box(width = 32, height = 32),
    )

    clock_layer = render.Row(
        children = [
            render.Box(width = 32, height = 32),
            right_clock,
        ],
    )

    return render.Root(
        delay = frame_delay,
        child = render.Stack(
            children = [
                # Foreground text layer (Rows 4 & 5 emerge from the curve beside the clock)
                left_column,
                # Clock layer on top: transparent outside bezel, perfect circular dial on right half
                clock_layer,
            ],
        ),
    )
