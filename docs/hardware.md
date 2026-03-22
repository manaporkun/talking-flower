# Hardware Guide

## Bill of Materials

| Item | Purpose | Status |
|------|---------|--------|
| Nintendo Talking Flower toy | Enclosure, button, speaker | Done |
| Raspberry Pi Zero 2 WH | Brain (pre-soldered headers) | Done |
| Dupont jumper wires (M-F, M-M, F-F) | Connecting components to Pi GPIO | Done |
| Soldering iron set | Solder wires to toy's sub-board | Done |
| Multimeter | Identify button pins, check speaker | Done |
| Micro-USB OTG adapter | USB devices to Pi | Done |
| MAX98357A I2S amplifier/DAC | Speaker output via I2S GPIO (no USB needed) | Ordered |
| INMP441 I2S MEMS microphone | Mic input via I2S GPIO (no USB needed) | Ordered |

### No longer needed

| Item | Reason |
|------|--------|
| USB sound card (UGREEN) | Replaced by I2S amp + mic |
| PAM8403 amplifier | MAX98357A has built-in amp |
| 3.5mm microphone | Replaced by INMP441 I2S mic |

## Architecture

All audio goes through the Pi's GPIO via I2S — no USB audio at all:

```
INMP441 mic ──(I2S)──> Pi GPIO ──(I2S)──> MAX98357A ──> Toy speaker
                          │
                     Button (GPIO17)
```

## Toy PCB Layout

The toy has two PCBs connected by a 6-wire ribbon cable:

### TAF-MAIN-01 (Main Board) — BYPASSED
- Contains the original processor, memory, audio codec
- **Disconnect the ribbon cable from this board** — the Pi replaces it entirely

### TAF-SUB-01 (Sub Board) — KEEPING
- **Tactile button**: Bottom-right, 2-pin momentary switch (the flower's press button)
- **Speaker wires**: Red (+) and black (-) at center-left, go to speaker in flower head
- **LED pads**: Row of contacts along bottom edge (for future lighting effects)

## Wiring

### Button → Pi GPIO (DONE)

1. Identified button legs with multimeter continuity mode
2. Soldered two wires to button pads on TAF-SUB-01
3. Attached female Dupont connectors
4. Connected to Pi:
   - One wire → **GPIO17** (physical pin 11)
   - Other wire → **GND** (physical pin 9)
5. Software uses internal pull-up — button press pulls GPIO LOW

### MAX98357A (Speaker Output) → Pi GPIO

| MAX98357A Pin | Pi Pin |
|---------------|--------|
| BCLK | GPIO18 (pin 12) |
| LRC | GPIO19 (pin 35) |
| DIN | GPIO21 (pin 40) |
| GND | GND (pin 6) |
| VIN | 5V (pin 2) |

Then connect MAX98357A speaker output (+/-) to the toy's speaker wires (red/black from TAF-SUB-01).

### INMP441 (Microphone Input) → Pi GPIO

| INMP441 Pin | Pi Pin |
|-------------|--------|
| SCK | GPIO18 (pin 12) — shared with MAX98357A BCLK |
| WS | GPIO19 (pin 35) — shared with MAX98357A LRC |
| SD | GPIO20 (pin 38) |
| VDD | 3.3V (pin 1) |
| GND | GND (pin 14) |
| L/R | GND (for left channel) |

**Note:** SCK and WS pins are shared between the amp and mic — this is normal for I2S.

### Enabling I2S on the Pi

```bash
# Add to /boot/firmware/config.txt:
dtoverlay=googlevoicehat-soundcard  # or hifiberry-dac for MAX98357A
# For INMP441, also add:
dtoverlay=i2s-mmap

# Reboot
sudo reboot
```

Exact overlay configuration may need tuning — will be finalized when boards arrive.

## Current Progress

| Step | Status |
|------|--------|
| Install PicoClaw on Pi | Done |
| Open toy and photograph PCBs | Done |
| Solder wires to button on TAF-SUB-01 | Done |
| Connect button to Pi GPIO17 | Done |
| Test button via GPIO | Done |
| Connect speaker to USB sound card (temp) | Done |
| Test audio output via USB | Done |
| Wire MAX98357A for I2S speaker output | Waiting for parts |
| Wire INMP441 for I2S mic input | Waiting for parts |
| Enable I2S overlays on Pi | Waiting for parts |
| Test full loop (button → voice → response → speaker) | Waiting for parts |
| Final assembly inside toy | Waiting for parts |
| Optional: Reuse LED pads for effects | Future |
