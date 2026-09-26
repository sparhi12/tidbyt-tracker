"""
Tidbyt renderer and publisher.
Executes Pixlet to render the Starlark template and pushes the resulting WebP
to the physical Tidbyt device via the official Tidbyt REST API.
"""

import base64
import logging
import os
import subprocess
from typing import Dict
import requests

logger = logging.getLogger(__name__)

class TidbytClient:
    PUSH_ENDPOINT = "https://api.tidbyt.com/v0/devices/{device_id}/push"

    def __init__(self, device_id: str, api_key: str, installation_id: str = "FlightTracker", pixlet_bin: str = "pixlet"):
        self.device_id = device_id
        self.api_key = api_key
        self.installation_id = installation_id
        self.pixlet_bin = pixlet_bin
        self.session = requests.Session()

    def render(self, star_path: str, output_path: str, fields: Dict[str, str], clock_b64: str) -> bool:
        """
        Execute Pixlet CLI to render the Starlark template with provided fields into output_path (WebP).
        """
        if not os.path.exists(star_path):
            logger.error(f"Starlark template not found at {star_path}")
            return False

        # Build CLI command with parameters passed via key=value config
        cmd = [
            self.pixlet_bin,
            "render",
            star_path,
            f"flight_no={fields.get('flight_no', 'SCANNING')}",
            f"airline={fields.get('airline', 'Seattle')}",
            f"row3_text={fields.get('row3_text', 'NW -> 0.1m')}",
            f"route_codes={fields.get('route_codes', 'SEA > ---')}",
            f"route_cities={fields.get('route_cities', 'Seattle')}",
            f"clock_b64={clock_b64}",
            "-o",
            output_path,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8.0)
            if res.returncode != 0:
                logger.error(f"Pixlet render failed: {res.stderr}")
                return False
            return True
        except FileNotFoundError:
            logger.error(f"Pixlet executable '{self.pixlet_bin}' not found on system PATH.")
            return False
        except Exception as e:
            logger.error(f"Error executing Pixlet render: {e}")
            return False

    def push(self, image_path: str) -> bool:
        """
        Push rendered WebP file to Tidbyt physical device using the REST API.
        """
        if not self.device_id or not self.api_key:
            logger.warning("TIDBYT_DEVICE_ID or TIDBYT_API_KEY is missing. Skipping push to device.")
            return False

        if not os.path.exists(image_path):
            logger.error(f"Image file to push not found: {image_path}")
            return False

        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()

            b64_image = base64.b64encode(img_bytes).decode("utf-8")
            url = self.PUSH_ENDPOINT.format(device_id=self.device_id)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "image": b64_image,
                "installationID": self.installation_id,
                "background": False,
            }

            resp = self.session.post(url, json=payload, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                logger.info(f"Successfully pushed frame to Tidbyt ({self.device_id}).")
                return True
            else:
                logger.error(f"Tidbyt push API returned status {resp.status_code}: {resp.text}")
                return False

        except Exception as e:
            logger.error(f"Failed to push image to Tidbyt: {e}")
            return False
