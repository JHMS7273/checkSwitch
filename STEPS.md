# SwitchCheck — Step-by-Step Setup (Raspberry Pi 5 + Sound Sensor)

Follow these steps in order. You need a **Raspberry Pi 5**, a **KY-038** (or similar) sound sensor, and **3 jumper wires**.

---

## Step 1 — Gather hardware

| Item | Notes |
|------|-------|
| Raspberry Pi 5 | Powered off for wiring |
| KY-038 sound sensor | 4 pins: VCC, GND, DO, AO |
| 3× female-to-female jumper wires | For VCC, GND, DO |
| Small screwdriver | To adjust the blue potentiometer on the sensor |

You only need **3 wires** for the basic setup (AO is not used).

---

## Step 2 — Wire the sensor to the Pi

Power off the Pi before connecting wires.

| Sensor pin | Wire to Pi 5 | Physical pin # |
|------------|--------------|----------------|
| **VCC** | 3.3V | **1** |
| **GND** | GND | **6** |
| **DO** | GPIO 17 | **11** |

```
Pi 5 (USB ports facing you)

     3.3V [ 1] [ 2] 5V
          [ 3] [ 4] 5V
          [ 5] [ 6] GND  ←── sensor GND
          [ 7] [ 8]
GPIO17   [11] [12]      ←── sensor DO
```

> Use **3.3V** (pin 1), **not** 5V.

---

## Step 3 — Power on and calibrate

1. Boot the Pi with the sensor connected.
2. Find the **blue potentiometer** on the sensor module.
3. Clap or speak loudly near the sensor.
4. Turn the potentiometer until the **onboard LED** lights up when sound is loud.
5. Adjust so normal room noise does **not** trigger the LED.

---

## Step 4 — Copy the project to the Pi

On your **Mac/PC**, copy the project folder to the Pi (replace `<PI_IP>` with your Pi's IP address):

```bash
scp -r /Users/adminn/Desktop/projects/switchcheck pi@<PI_IP>:~/
```

Find your Pi IP on the Pi with:

```bash
hostname -I
```

---

## Step 5 — Install dependencies on the Pi

SSH into the Pi:

```bash
ssh pi@<PI_IP>
```

Then run:

```bash
cd ~/switchcheck
sudo apt update
sudo apt install -y python3-pip python3-venv python3-lgpio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 6 — Run the sound sensor script

With the virtual environment active:

```bash
cd ~/switchcheck
source .venv/bin/activate
python sound_sensor.py
```

Expected output when you make noise:

```
Sound sensor monitor started
  GPIO (BCM): 17
  Debounce:   50 ms
  ...
[14:30:01] SOUND DETECTED
[14:30:02] quiet
```

Press **Ctrl+C** to stop.

---

## Step 7 — Optional flags

```bash
# Only print when sound is detected
python sound_sensor.py --quiet

# Use a different GPIO pin (if you wired DO elsewhere)
python sound_sensor.py --pin 27
```

---

## Step 8 — Optional: analog loudness (advanced)

Skip this unless you need a numeric sound level (0.0–1.0).

1. Add an **MCP3008** ADC between the Pi and sensor.
2. Connect sensor **AO** to MCP3008 **CH0**.
3. Wire MCP3008 to Pi SPI pins (see `README.md`).
4. Enable SPI:

   ```bash
   sudo raspi-config
   # Interface Options → SPI → Enable
   sudo reboot
   ```

5. Run:

   ```bash
   source .venv/bin/activate
   python sound_sensor_analog.py
   ```

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| `No module named lgpio` | Run `sudo apt install python3-lgpio` then `pip install lgpio` |
| Always says SOUND DETECTED | Turn potentiometer counter-clockwise; check GND wire |
| Never detects sound | Turn potentiometer clockwise; check DO wire on pin 11 |
| Cannot SSH to Pi | Check Pi is on the same network; verify IP with `hostname -I` |
| Permission error on GPIO | Use the `pi` user; do not run with `sudo` |

---

## Checklist

- [ ] Step 1 — Hardware ready
- [ ] Step 2 — VCC → 3.3V, GND → GND, DO → GPIO 17
- [ ] Step 3 — Potentiometer calibrated
- [ ] Step 4 — Project copied to Pi
- [ ] Step 5 — Dependencies installed
- [ ] Step 6 — `python sound_sensor.py` runs and detects sound
