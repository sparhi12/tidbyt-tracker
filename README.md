# ✈️ Tidbyt Flight Tracker (Gen 1)

A high-performance, resilient flight tracking system for the **Tidbyt Gen 1** (64x32 RGB LED matrix) running on a free Google Cloud Platform (GCP) `e2-micro` VM, automated with a GitHub-controlled deployment system.

---

## 📺 Display Layout (64x32 Pixels)

The screen is split into two 32x32 pixel halves:

```
+--------------------------------+--------------------------------+
| AS1762                         |             __--__             |
| Alaska Airlines                |            /  12  \            |
| NW -> 0.1m                     |           | 9  •   3|          |
| PDX > LAX                      |            \   6  /            |
| Portland > Los Angeles         |             ^--__^             |
+--------------------------------+--------------------------------+
      Left Half (32x32)                  Right Half (32x32)
       Flight Information                    Analog Clock
```

### Left Half (5 Rows):
1. **Row 1**: Flight Number (e.g. `AS1762`) in gold (`#FFD700`).
2. **Row 2**: Airline Name (e.g. `Alaska Airlines`) with smooth Marquee scroll in sky blue (`#38BDF8`).
3. **Row 3**: 8-point compass direction & distance relative to Denny Way & Westlake Ave Seattle formatted as **`NW -> 0.1m`** in green (`#4ADE80`). Strictly static without scrolling.
4. **Row 4**: Origin > Destination IATA codes (e.g. `PDX > LAX`) in amber (`#FB923C`).
5. **Row 5**: Origin > Destination full city names (e.g. `Portland > Los Angeles`) with Marquee scroll in soft white (`#E2E8F0`).

### Right Half:
- **Real-Time 32x32 Analog Clock**: Generated dynamically with bezel rim, cardinal hour ticks (12, 3, 6, 9), white hour hand, cyan minute hand, and crimson second hand.

### Standby Mode:
When no aircraft are in the overhead airspace, the Tidbyt displays:
- Row 1: `SEATTLE`
- Row 2: `Clear Sky`
- Row 3: `NW -> 0.0m`
- Row 4: `SEA AREA`
- Row 5: `Denny & Westlake`
- Right Half: Analog clock continues showing live real-time hours, minutes, and seconds.

---

## 🧭 Flight Selection & Priority

- **Target Location**: Denny Way & Westlake Ave, Seattle (`47.6186° N, 122.3365° W`).
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
   git clone https://github.com/<your-username>/<your-repo-name>.git /opt/tidbyt-flight-tracker
   cd /opt/tidbyt-flight-tracker
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
```

### 4. Start the Service
```bash
sudo systemctl start tidbyt-tracker
sudo journalctl -u tidbyt-tracker -f
```

---

## 🔄 GitHub-Controlled Auto-Deployment

The GCP VM includes an automated systemd timer (`tidbyt-updater.timer`) that polls GitHub every 3 minutes.
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
| `MAX_RADIUS_MILES` | `15.0` | Maximum radius for tracking overhead aircraft |
| `POLL_INTERVAL_SECONDS`| `10` | Frequency of display updates on Tidbyt |
| `EASTERN_PRIORITY` | `true` | Prioritize aircraft in $0^\circ \le \theta \le 180^\circ$ (N $\to$ E $\to$ S) |
