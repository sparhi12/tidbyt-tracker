# ✈️ Tidbyt Flight Tracker (Gen 1)

A high-performance, resilient flight tracking system for the **Tidbyt Gen 1** (64x32 RGB LED matrix) running on a free Google Cloud Platform (GCP) `e2-micro` VM, automated with a GitHub-controlled deployment system.

---

## 📺 Display Layout (64x32 Pixels)

The screen is split into two 32x32 pixel halves:

```
+--------------------------------+--------------------------------+
| ASA1762                        |             __--__             |
| Nw 0.12                        |            /  12  \            |
| SEA->SFO                       |           | 9  •   3|          |
| Alaska                         |            \   6  /            |
| Seattle > San Francisco        |             ^--__^             |
+--------------------------------+--------------------------------+
      Left Half (32x32)                  Right Half (32x32)
       Flight Information                    Analog Clock
```

### Left Half (5 Rows - Flush Left):
1. **Row 1 (Static)**: Flight Number (e.g. `ASA1762`), anchored flush left with no gap.
2. **Row 2 (Static)**: 8-point compass direction & distance with 2 decimal places in miles (e.g. **`Nw 0.12`**, with lowercase `w` for West), anchored flush left.
3. **Row 3 (Static)**: Origin > Destination IATA codes (e.g. **`SEA->SFO`**), exactly 8 characters ($8 \times 4\text{px} = 32\text{px}$) filling the row up to $x=31$ without penetrating the clock bezel at $x=33$.
4. **Row 4 (Scrolling Marquee)**: Airline brand name (e.g. `Alaska`) with scrolling window extended to $x=34$ at the clock bezel edge.
5. **Row 5 (Scrolling Marquee)**: Origin > Destination full city names (e.g. `Seattle > San Francisco`) with scrolling window extended to $x=38$ into the curve under the clock. Both scrolling rows adaptively compute frame rate from fragment length and poll interval, ensuring long routes (e.g. `San Francisco > Portland`) display completely in 1 run.

### 🎨 Cohesive Color Palettes (8-Hour Time-of-Day Rotation):
To avoid jarring color clashes on the 64x32 LED matrix, a curated palette rotates every 8 hours based on local time (`America/Los_Angeles`):
- **Pacific Aviation (Day: 08:00 - 15:59)**: Crisp daytime sky blues, aquas, teals, and soft cloud mist (`#38BDF8`, `#2DD4BF`, `#22D3EE`, `#7DD3FC`, `#E2E8F0`).
- **Golden Sunset (Evening: 16:00 - 23:59)**: Warm, cozy amber, peach, coral, champagne, and warm cream (`#FBBF24`, `#FDBA74`, `#FB7185`, `#FDE047`, `#FEF3C7`).
- **Midnight Aurora (Night: 00:00 - 07:59)**: Soothing, low-glare mint jade, emerald, seafoam, lavender, and silver (`#34D399`, `#6EE7B7`, `#A7F3D0`, `#C084FC`, `#CBD5E1`).
*(Can be locked to a specific theme or overridden via `PALETTE_MODE` in `.env`).*

### Right Half:
- **Real-Time 32x32 Analog Clock**: Generated dynamically with pixel-perfect Euclidean circle dial, radial cardinal hour ticks (12, 3, 6, 9), 1-pixel red hour hand, 1-pixel sky blue minute hand, and 1-pixel light green ticking second hand updating live every 1s (`SHOW_SECOND_HAND=true`, `TIMEZONE=America/Los_Angeles`).

### Standby Mode:
When no aircraft are in the overhead airspace, the Tidbyt displays:
- Row 1: `SCANNING`
- Row 2: `Nw 0.00`
- Row 3: `SEA->---`
- Row 4: `Seattle Skies`
- Row 5: `Overhead Seattle`
- Right Half: Analog clock continues showing live real-time local hours, minutes, and seconds.

---

## 🧭 Flight Selection & Priority

- **Target Location**: Denny Way & Westlake Ave, Seattle (`47.6186° N, 122.3365° W`).
- **Default Radius**: `25.0` miles.
- **Eastern Hemisphere Priority**: Priority is given to aircraft in the North $\to$ East $\to$ South right hemisphere ($0^\circ \le \theta \le 180^\circ$). The closest aircraft in this sector is tracked. If no aircraft are in the eastern sector, the closest aircraft overall is chosen.

---

## ⚡ Zero-Cost GCP Free Tier Sizing ($0.00 / month)

Running on a standard GCP `e2-micro` VM (eligible for the Always Free Tier in `us-central1`, `us-west1`, or `us-east1`):

- **CPU**: **~0.7% load** (Python sleeps 9.9s out of every 10s; active cycle takes ~70ms).
- **RAM**: **~220 MB total** (OS: 150MB, Python: 40MB, Pixlet spike: 30MB) out of 1.0 GB available.
- **Disk**: **~2.8 GB total** out of 30 GB free persistent disk.
- **Network Egress**: **~380 MB / month** out of 1.0 GB free internet egress.

---

## 🚀 Quick Start Deployment Guide

### 1. Push Code to Your GitHub Repository
On your local machine:
```bash
git init
git add .
git commit -m "Initial commit of Tidbyt Flight Tracker"
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

### 2. Set Up the GCP `e2-micro` VM
1. Create a free VM on Google Cloud Console:
   - **Machine Type**: `e2-micro`
   - **Region**: `us-west1` (Oregon), `us-central1` (Iowa), or `us-east1` (South Carolina)
   - **OS**: Debian 12 or Ubuntu 22.04 LTS
   - **Disk**: 10 GB or 30 GB standard persistent disk
2. SSH into your VM and run:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git ~/tidbyt-tracker
   cd ~/tidbyt-tracker
   sudo ./deploy/setup_vm.sh
   ```

### 3. Configure Your Credentials
Edit `.env` on the VM:
```bash
nano .env
```
Fill in your credentials:
```ini
TIDBYT_DEVICE_ID=your_device_id_here
TIDBYT_API_KEY=your_tidbyt_api_key_here
OPENSKY_USERNAME=your_opensky_username
OPENSKY_PASSWORD=your_opensky_password
TIMEZONE=America/Los_Angeles
MAX_RADIUS_MILES=25.0
```

### 4. Start the Service
```bash
sudo systemctl start tidbyt-tracker
sudo journalctl -u tidbyt-tracker -f
```

---

## 🔄 GitHub-Controlled Auto-Deployment

The GCP VM includes an automated systemd timer (`tidbyt-updater.timer`) running as `root` that polls GitHub every 3 minutes.
- **Push any changes** (tweaking fonts, colors, layouts, or tracker settings) to `main`.
- Within 3 minutes, the VM automatically pulls the latest commit, reinstalls dependencies if `requirements.txt` changed, and restarts the tracker daemon!
- Requires **zero open firewall ports** or complex webhooks.

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TIDBYT_DEVICE_ID` | — | Your Tidbyt Device ID (from Tidbyt mobile app) |
| `TIDBYT_API_KEY` | — | Your Tidbyt API Token |
| `DATA_SOURCE` | `dual` | `dual` (tries airplanes.live, falls back to OpenSky), `airplanes_live`, or `opensky` |
| `OPENSKY_USERNAME` | — | OpenSky account username |
| `OPENSKY_PASSWORD` | — | OpenSky account password |
| `OPENSKY_POLL_INTERVAL`| `22` | Seconds between OpenSky calls (keeps under 4,000 credit/day limit) |
| `REF_LAT` | `47.6186` | Latitude of Denny & Westlake, Seattle |
| `REF_LON` | `-122.3365` | Longitude of Denny & Westlake, Seattle |
| `MAX_RADIUS_MILES` | `25.0` | Maximum radius in miles for tracking overhead aircraft |
| `TIMEZONE` | `America/Los_Angeles` | Timezone string for analog clock display |
| `POLL_INTERVAL_SECONDS`| `1` | Frequency of display updates on Tidbyt (1s real-time tracking) |
| `SHOW_SECOND_HAND` | `true` | Set to `true` for light green second hand on analog clock |
| `EASTERN_PRIORITY` | `true` | Prioritize aircraft in $0^\circ \le \theta \le 180^\circ$ (N $\to$ E $\to$ S) |
| `PALETTE_MODE` | `auto` | Color palette: `auto` (8-hour rotation: Day, Sunset, Night) or `day`, `sunset`, `night` |
