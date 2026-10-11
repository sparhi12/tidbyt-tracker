"""
Tidbyt Flight Tracker Display
Resolution: 64x32
Left Half (32x32): 5 rows of flight information (Flush left, no gap)
  Row 1 (Static): Flight Number
  Row 2 (Static): Direction & Distance
  Row 3 (Static): Route Codes
  Row 4 (Scrolling): Airline Name (Adaptive scroll speed based on poll interval)
  Row 5 (Scrolling): Route Cities (Adaptive scroll speed based on poll interval)
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

    # Adaptive scroll rate based on polling interval (e.g. 1000ms -> 20ms frame delay = 50 fps)
    poll_interval_ms = int(config.get("poll_interval_ms", "1000"))
    frame_delay = max(15, min(80, poll_interval_ms // 50))

    # Pleasing, cohesive color palette (rotates on 8-hour day/sunset/night schedule)
    color_row1 = config.get("color_row1", "#38BDF8").strip()
    color_row2 = config.get("color_row2", "#2DD4BF").strip()
    color_row3 = config.get("color_row3", "#22D3EE").strip()
    color_row4 = config.get("color_row4", "#7DD3FC").strip()
    color_row5 = config.get("color_row5", "#E2E8F0").strip()

    # Left Column: exactly 32px wide x 32px high, containing 5 rows (6px each)
    # Rows 1, 2 & 3 are anchored flush to the left edge (x=0) without left padding or Box centering.
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
            # Row 3: Route Codes (Static, e.g. "SEA>SFO", Flush Left)
            render.Text(
                content = route_codes,
                font = "tom-thumb",
                color = color_row3,
            ),
            # Row 4: Airline Name (Marquee fast scroll, Adaptive)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
                    delay = 0,
                    child = render.Text(
                        content = airline,
                        font = "tom-thumb",
                        color = color_row4,
                    ),
                ),
            ),
            # Row 5: Origin > Destination Full City Names (Marquee fast scroll, Adaptive)
            render.Box(
                width = 32,
                height = 6,
                child = render.Marquee(
                    width = 32,
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

    # Right side: 32x32 analog clock image
    right_clock = render.Box(
        width = 32,
        height = 32,
        child = render.Image(src = base64.decode(clock_b64)) if clock_b64 else render.Box(width = 32, height = 32),
    )

    return render.Root(
        delay = frame_delay,
        child = render.Row(
            children = [
                render.Box(width = 32, height = 32, child = left_column),
                right_clock,
            ],
        ),
    )
