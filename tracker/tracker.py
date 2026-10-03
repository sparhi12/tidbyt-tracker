"""
Tidbyt Flight Tracker Main Daemon.
Coordinates flight tracking, analog clock generation, Pixlet rendering,
and Tidbyt API push on a precise 10-second loop.
"""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import signal
import sys
import time

from tracker.clock import generate_analog_clock
from tracker.config import Config
from tracker.flight_service import FlightService
from tracker.tidbyt import TidbytClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("tracker")

class FlightTrackerDaemon:
    def __init__(self, dry_run: bool = False):
        self.config = Config()
        self.dry_run = dry_run
        self.flight_service = FlightService(self.config)
        self.tidbyt = TidbytClient(
            device_id=self.config.TIDBYT_DEVICE_ID,
            api_key=self.config.TIDBYT_API_KEY,
            installation_id=self.config.TIDBYT_INSTALLATION_ID,
            pixlet_bin=self.config.PIXLET_BIN,
        )
        self._running = True

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._running = False

    def step(self) -> bool:
        """
        Execute a single tracking, rendering, and push cycle.
        """
        start_time = time.time()
        try:
            tz = ZoneInfo(self.config.TIMEZONE)
            now_dt = datetime.now(tz)
        except Exception:
            now_dt = datetime.now()

        # 1. Generate 32x32 analog clock PNG
        clock_b64 = generate_analog_clock(now_dt, show_second_hand=self.config.SHOW_SECOND_HAND)

        # 2. Get latest flight data
        flight_data = self.flight_service.get_current_display_data()
        logger.info(
            f"Active Flight: {flight_data['flight_no']} | Airline: {flight_data['airline']} | "
            f"Row 3: {flight_data['row3_text']} | Route: {flight_data['route_codes']} ({flight_data['route_cities']})"
        )

        if self.dry_run:
            logger.info("Dry-run mode: skipping Pixlet rendering and Tidbyt push.")
            return True

        # 3. Render display via Pixlet
        render_ok = self.tidbyt.render(
            star_path=self.config.STAR_PATH,
            output_path=self.config.OUTPUT_IMAGE,
            fields=flight_data,
            clock_b64=clock_b64,
        )

        if not render_ok:
            logger.warning("Pixlet rendering was unsuccessful.")
            return False

        # 4. Push to Tidbyt physical device
        push_ok = self.tidbyt.push(self.config.OUTPUT_IMAGE)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Cycle completed in {duration_ms:.1f}ms (Push: {push_ok})")
        return push_ok

    def run(self):
        """
        Continuous daemon loop running every POLL_INTERVAL_SECONDS (default 10s).
        """
        logger.info(f"Starting Tidbyt Flight Tracker daemon (Interval: {self.config.POLL_INTERVAL_SECONDS}s)...")
        logger.info(f"Reference Point: ({self.config.REF_LAT}, {self.config.REF_LON}) | Source: {self.config.DATA_SOURCE}")

        while self._running:
            loop_start = time.time()
            try:
                self.step()
            except Exception as e:
                logger.error(f"Unexpected error in tracking cycle: {e}", exc_info=True)

            elapsed = time.time() - loop_start
            sleep_time = max(0.0, self.config.POLL_INTERVAL_SECONDS - elapsed)
            if self._running and sleep_time > 0:
                time.sleep(sleep_time)

        logger.info("Flight Tracker daemon has terminated.")

def main():
    parser = argparse.ArgumentParser(description="Tidbyt Flight Tracker Daemon")
    parser.add_argument("--once", action="store_true", help="Execute single cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and process without Pixlet render or Tidbyt push")
    parser.add_argument("--test", action="store_true", help="Run self-test with sample flight data")
    args = parser.parse_args()

    daemon = FlightTrackerDaemon(dry_run=args.dry_run)

    if args.test:
        logger.info("Running self-test with simulated flight...")
        clock_b64 = generate_analog_clock(show_second_hand=daemon.config.SHOW_SECOND_HAND)
        test_data = {
            "flight_no": "AS1762",
            "airline": "Alaska",
            "row3_text": "NW -> 0.1m",
            "route_codes": "PDX > LAX",
            "route_cities": "Portland > Los Angeles",
            "is_active": "true"
        }
        daemon.tidbyt.render(
            star_path=daemon.config.STAR_PATH,
            output_path=daemon.config.OUTPUT_IMAGE,
            fields=test_data,
            clock_b64=clock_b64
        )
        logger.info(f"Self-test render saved to {daemon.config.OUTPUT_IMAGE}")
        sys.exit(0)

    if args.once:
        daemon.step()
    else:
        daemon.run()

if __name__ == "__main__":
    main()
