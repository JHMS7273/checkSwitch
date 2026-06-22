# SwitchCheck — Sound Sensor (Raspberry Pi 5)

Starter project for a **KY-038** (or similar LM393) sound sensor on Raspberry Pi 5.

## Wiring (digital mode — recommended to start)

Connect the sensor to the Pi **40-pin header**:

| Sensor pin | Connect to Pi 5 | Physical pin # |
|------------|-----------------|----------------|
| **VCC**    | 3.3V            | Pin 1          |
| **GND**    | GND             | Pin 6          |
| **DO**     | GPIO 17 (BCM)   | Pin 11         |
| **AO**     | *(not used)*    | —              |

```
Pi 5 (top view, USB ports facing you)

     3.3V [ 1] [ 2] 5V
          [ 3] [ 4] 5V
          [ 5] [ 6] GND  ←── GND
          [ 7] [ 8]
     GND  [ 9] [10]
GPIO17   [11] [12]      ←── DO
          ...
```

> **Important:** Use **3.3V**, not 5V, unless your module documentation explicitly says 5V.

### Calibrate the sensor

1. Power the Pi with the sensor connected.
2. Turn the **blue potentiometer** on the module with a small screwdriver.
3. Clap or make noise — the onboard LED should blink when sound exceeds the threshold.
4. Set it so normal room noise stays quiet and your target sound triggers the LED.

## Setup on the Pi

```bash
# On the Raspberry Pi (not your Mac/PC)
sudo apt update
sudo apt install -y python3-pip python3-venv python3-lgpio

cd ~/switchcheck   # copy this folder to the Pi first
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the project to the Pi (from your computer):

```bash
scp -r /path/to/switchcheck pi@<PI_IP>:~/
```

## Run

### Digital sensor (DO pin) — start here

```bash
source .venv/bin/activate
python sound_sensor.py
```

Custom GPIO pin:

```bash
python sound_sensor.py --pin 27
```

Only print when sound is detected:

```bash
python sound_sensor.py --quiet
```

### Analog sensor (AO + MCP3008) — optional

If you need a numeric loudness value, add an **MCP3008** ADC:

| MCP3008 | Pi 5        | Physical pin |
|---------|-------------|--------------|
| VDD     | 3.3V        | 1            |
| VREF    | 3.3V        | 1            |
| AGND    | GND         | 6            |
| DGND    | GND         | 6            |
| CLK     | GPIO 11     | 23           |
| DOUT    | GPIO 9      | 21           |
| DIN     | GPIO 10     | 19           |
| CS      | GPIO 8      | 24           |
| CH0     | Sensor **AO** | —          |

Enable SPI once:

```bash
sudo raspi-config   # Interface Options → SPI → Enable
sudo reboot
```

Then run:

```bash
python sound_sensor_analog.py
python sound_sensor_analog.py --threshold 0.2
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named lgpio` | `sudo apt install python3-lgpio` then `pip install lgpio` |
| Always shows SOUND DETECTED | Turn potentiometer counter-clockwise; check GND connection |
| Never detects sound | Turn potentiometer clockwise; verify DO → GPIO 17 |
| Permission errors | Run with your `pi` user (gpiozero handles permissions on Pi OS) |

## Project layout

```
switchcheck/
├── STEPS.md                # Step-by-step setup guide (start here)
├── sound_sensor.py         # Digital (DO) — main script
├── sound_sensor_analog.py  # Analog (AO + MCP3008) — optional
├── requirements.txt
└── README.md
```
