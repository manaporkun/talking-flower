# Hardware Guide

## Bill of Materials

| Item | Purpose | Approx. Cost |
|------|---------|--------------|
| Nintendo Talking Flower toy | Enclosure, button, speaker | ~$15 |
| Raspberry Pi Zero 2 WH | Brain (pre-soldered headers) | ~$20 |
| USB sound card (UGREEN or similar) | Audio I/O (Pi Zero has none) | ~$8 |
| Micro-USB OTG adapter | Connect USB sound card to Pi | ~$3 |
| Dupont jumper wires (M-F) | Button to GPIO, no soldering on Pi side | ~$3 |
| Soldering iron + solder | Solder wires to toy's sub-board | ~$15 |
| Multimeter | Identify button pins, check speaker | ~$10 |
| PAM8403 amplifier (optional) | Boost speaker volume | ~$2 |
| Microphone (USB or 3.5mm) | Voice input | ~$5 |

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

### Button → Pi GPIO

1. Use multimeter continuity mode to find which two button legs close on press
2. Solder two wires to those pads on TAF-SUB-01
3. Attach female Dupont connectors to the other end
4. Connect to Pi:
   - One wire → **GPIO17** (physical pin 11)
   - Other wire → **GND** (physical pin 9)
5. Software uses internal pull-up — button press pulls GPIO LOW

### Speaker → USB Sound Card

1. The red/black speaker wires on TAF-SUB-01 are your speaker connection
2. Cut a 3.5mm audio cable, strip the wires
3. Connect speaker red/black to cable's audio + ground
4. Plug into USB sound card headphone output

**Note:** The toy speaker is small (~8 ohm). USB sound card output may be quiet.
Add a PAM8403 mini amplifier between the sound card and speaker for proper volume.

### USB Sound Card → Pi

- Plug into Pi Zero's **data** micro-USB port (not power port!)
- Use micro-USB OTG adapter if needed

## Audio Device Note

USB audio card numbers change between reboots. The voice assistant script
auto-detects devices by name (using `INPUT_DEVICE_HINT` and `OUTPUT_DEVICE_HINT`
in `.env`), so this is handled automatically.
