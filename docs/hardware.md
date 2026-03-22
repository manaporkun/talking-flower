# Hardware Guide

## Bill of Materials

| Item | Purpose | Status |
|------|---------|--------|
| Nintendo Talking Flower toy | Enclosure, button, speaker | Done |
| Raspberry Pi Zero 2 WH (512 MB, 1 GHz) | Brain (pre-soldered headers) | Done |
| Elegoo 120pcs Dupont jumper wires (M-F, M-M, F-F) | Connecting components | Done |
| Soldering iron set (80W, LCD, 180-520C) | Solder wires to toy's sub-board | Done |
| AstroAI digital multimeter | Identify pins, check speaker impedance | Done |
| Micro-USB OTG adapter | USB devices to Pi | Done |
| MAX98357A I2S amplifier/DAC | Speaker output via I2S GPIO (replaces UGREEN) | Ordered |
| INMP441 I2S MEMS microphone | Mic input via I2S GPIO | Ordered |

### Previously used (being replaced)

| Item | Replaced by |
|------|-------------|
| UGREEN USB sound card | MAX98357A (output) + INMP441 (input) |

## Architecture

All audio goes through the Pi's GPIO via I2S — no USB audio:

```
INMP441 mic ──(I2S)──> Pi GPIO ──(I2S)──> MAX98357A ──> Toy speaker
                          │
                     Button (GPIO17)
                     (dome switch on TAF-SUB-01)
```

## Toy PCB Details

The toy has two PCBs connected by a 6-wire ribbon cable.

### TAF-MAIN-01 — Main Board (BYPASSED)

- **Photos:** IMG_2557.HEIC (Side A), IMG_2558.HEIC (Side B)
- Side A: Main processor IC (QFP package), two smaller ICs (memory/audio codec), passives. Labeled "SIDE-A", "TAF-MAIN-01", date code "2B25".
- Side B: QR code serial "0A05 3765 T01M 00540". Gold edge connector strip (~10 contacts) for ribbon cable.
- **Action:** Ribbon cable desoldered from this board. Board is no longer used.

### TAF-SUB-01 — Sub Board (KEEPING)

- **Photos:** IMG_2559.HEIC (component side), IMG_2582.HEIC (trace side with Dupont wires)
- **Button:** NOT a tactile push switch. It's a **cross-shaped open contact pad** (dome switch) — two concentric contact areas bridged by a conductive rubber dome in the toy's plastic housing when pressed.
- **Speaker wires:** Red (+) and black (-) soldered to board pads. These are independent of the ribbon cable but connect through PCB traces to the ribbon cable pads.
- **Row of gold pads** along bottom edge — purpose unconfirmed (possibly LEDs or battery contacts).
- **Ribbon cable:** Original 6-wire cable desoldered from TAF-MAIN-01. 5 Dupont wires soldered to the ribbon cable pads on TAF-SUB-01.

## Wire Map (Confirmed by Multimeter)

| Dupont Wire Color | Function | How Confirmed |
|-------------------|----------|---------------|
| **Black** | Button (side 1) | Continuity with button contact pad |
| **White** | Button (side 2) | Continuity with button contact pad |
| **Purple** | Speaker (one side) | Resistance: purple+gray reads 7-16 ohm (8 ohm speaker coil) |
| **Gray** | Speaker (other side) | Same as above |
| **Blue** | Unknown | Not button, not speaker. Possibly battery/power or LED. |

**Key findings:**
- The speaker IS routed through the ribbon cable via purple and gray wires
- The red/black wires on the board connect through PCB traces to purple/gray Dupont wires
- Button press bridges Black and White wires together
- Speaker impedance: ~8 ohm

## Current Wiring (DONE)

### Button → Pi GPIO

- **Black** Dupont wire → **GPIO17** (physical pin 11)
- **White** Dupont wire → **GND** (physical pin 9)
- Software uses internal pull-up. Button press shorts Black+White, pulling GPIO17 to GND.
- Tested and working with gpiozero.

### Speaker → UGREEN (Temporary, will be replaced by MAX98357A)

Connected via a cut headphone cable:
- **Copper** headphone wire soldered to **purple** Dupont wire
- **Red** headphone wire soldered to **gray** Dupont wire
- Blue headphone wire unused
- 3.5mm plug into UGREEN headphone output
- Volume is low without amplifier — MAX98357A will fix this

## Future Wiring (When I2S parts arrive)

### MAX98357A (Speaker Output) → Pi GPIO

| MAX98357A Pin | Pi Pin |
|---------------|--------|
| BCLK | GPIO18 (pin 12) |
| LRC | GPIO19 (pin 35) |
| DIN | GPIO21 (pin 40) |
| GND | GND (pin 6) |
| VIN | 5V (pin 2) |

Then connect MAX98357A speaker output (+/-) to **purple** and **gray** Dupont wires (which connect to the toy speaker through TAF-SUB-01 traces).

### INMP441 (Microphone Input) → Pi GPIO

| INMP441 Pin | Pi Pin |
|-------------|--------|
| SCK | GPIO18 (pin 12) — shared with MAX98357A BCLK |
| WS | GPIO19 (pin 35) — shared with MAX98357A LRC |
| SD | GPIO20 (pin 38) |
| VDD | 3.3V (pin 1) |
| GND | GND (pin 14) |
| L/R | GND (for left channel) |

### Enabling I2S on the Pi

```bash
# Add to /boot/firmware/config.txt
dtoverlay=googlevoicehat-soundcard  # or hifiberry-dac for MAX98357A

# Reboot
sudo reboot
```

Exact overlay configuration will be finalized when boards arrive.

## Progress

| Step | Status |
|------|--------|
| Acquire hardware | Done |
| Install PicoClaw on Pi | Done |
| Open toy and photograph PCBs | Done (4 photos) |
| Desolder ribbon cable from TAF-MAIN-01 | Done |
| Solder 5 Dupont wires to TAF-SUB-01 pads | Done |
| Identify all wire functions with multimeter | Done |
| Connect button to Pi GPIO17 | Done |
| Test button via GPIO | Done |
| Connect speaker to UGREEN (temporary) | Done |
| Test audio output | Done (low volume without amp) |
| Voice assistant software | Done |
| PicoClaw integration + character | Done |
| Wire MAX98357A for I2S speaker output | Waiting for parts |
| Wire INMP441 for I2S mic input | Waiting for parts |
| Enable I2S overlays on Pi | Waiting for parts |
| Test full loop (button → voice → response → speaker) | Waiting for parts |
| Final assembly inside toy | Waiting for parts |
| Figure out blue wire function | Future |
| Reuse LED pads for effects | Future |

## Key Warnings

1. **The button is NOT a tactile switch** — it's open contact pads (cross-shaped dome switch). A rubber dome in the toy housing bridges the contacts when pressed.
2. **The speaker IS routed through the ribbon cable** via purple and gray Dupont wires, not directly from the red/black wires.
3. **Pi Zero 2 WH has pre-soldered headers** — no soldering on Pi side, use Dupont wires.
4. **Pi has only 416 MB RAM** — don't run multiple heavy processes simultaneously.
5. **USB audio card numbers change on reboot** — the voice assistant auto-detects by name.
6. **TAF-MAIN-01 is fully bypassed** — don't waste time on it.
