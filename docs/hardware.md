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
| Google AIY VoiceHAT v1 | Provides MAX98357A I2S amp (speaker) + mic (unused) | Done |
| USB Audio Device (C-Media) | Temporary mic input until INMP441 arrives | Done |
| INMP441 I2S MEMS microphone | Mic input via I2S GPIO (will replace USB mic) | Ordered |

### Previously used (being replaced)

| Item | Replaced by |
|------|-------------|
| UGREEN USB sound card | MAX98357A (output) + INMP441 (input, pending) |

### Current temporary setup

| Item | Purpose | Card |
|------|---------|------|
| Google AIY VoiceHAT v1 | Provides MAX98357A I2S amp for speaker output | card 1 (MAX98357A) |
| USB Audio Device (C-Media) | Mic input (temporary until INMP441 arrives) | card 0 |

## Architecture

Speaker output via I2S (MAX98357A on VoiceHAT), mic input via USB:

```
USB C-Media mic ──(USB)──> Pi ──(I2S)──> MAX98357A (VoiceHAT) ──> Toy speaker
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
# /boot/firmware/config.txt
dtparam=i2s=on
dtoverlay=max98357a          # Clean MAX98357A driver (NOT googlevoicehat-soundcard)
```

**IMPORTANT:** Do NOT use `dtoverlay=googlevoicehat-soundcard`. The VoiceHAT driver has its
own amp enable/disable codec (`voicehat-codec`) that causes cracking and popping. The clean
`max98357a` overlay drives the same hardware without the codec overhead.

### ALSA Configuration (~/.asoundrc)

The Pi Zero 2W has a known over-amplification bug with MAX98357A — audio is pushed too hot
at the I2S level. The fix is a `softvol` ALSA layer to attenuate the signal:

```
pcm.dmixer {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:1,0"              # MAX98357A card (check with aplay -l)
        period_size 2048
        buffer_size 16384
        rate 48000
        channels 1                # MAX98357A is MONO — stereo causes crackling
        format S32_LE
    }
}

pcm.softvol {
    type softvol
    slave.pcm "dmixer"
    control { name "SoftMaster"; card 1 }
    min_dB -40.0
    max_dB 0.0
}

pcm.speaker {
    type plug
    slave.pcm "softvol"
}
```

Key points:
- **dmix** allows multiple audio streams (silence streamer + actual audio) to share the device
- **softvol** at ~90% (value 230/255) tames the Pi Zero 2W over-amplification
- **channels 1** is critical — the toy has a single mono speaker; sending stereo causes artifacts
- A background silence streamer (`aplay -D speaker -f S16_LE -r 48000 -c 1 /dev/zero`)
  keeps the I2S clock running so the amp never powers off (prevents power-on/off pop)

### USB Mic (C-Media) Settings

```bash
# Max capture volume (+23dB) — the default is too quiet
amixer -c 0 cset numid=8 35

# Enable Auto Gain Control
amixer -c 0 cset numid=9 1

# Persist across reboots
sudo alsactl store
```

The voice assistant pipeline also applies: highpass filter (200Hz, removes hum) +
noise gate (suppresses background noise) + normalization before sending to STT.

### Audio Card Numbers (after reboot with max98357a overlay)

Card numbers are assigned by the kernel at boot and may change if USB devices are
unplugged/replugged. Current layout:

| Card | Device | Used for |
|------|--------|----------|
| 0 | USB Audio Device (C-Media) | Mic input |
| 1 | MAX98357A | Speaker output (I2S) |
| 2 | vc4-hdmi | HDMI audio (unused) |

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
| Connect speaker via MAX98357A I2S amp | Done |
| Voice assistant software | Done |
| PicoClaw integration + character | Done |
| Full loop (button -> voice -> response -> speaker) | Done |
| Audio quality tuning (mono, softvol, noise gate) | Done |
| Wire INMP441 for I2S mic input | Waiting for parts |
| Final assembly inside toy | Future |
| Figure out blue wire function | Future |
| Reuse LED pads for effects | Future |

## Key Warnings

1. **The button is NOT a tactile switch** — it's open contact pads (cross-shaped dome switch). A rubber dome in the toy housing bridges the contacts when pressed.
2. **The speaker IS routed through the ribbon cable** via purple and gray Dupont wires, not directly from the red/black wires.
3. **Pi Zero 2 WH has pre-soldered headers** — no soldering on Pi side, use Dupont wires.
4. **Pi has only 416 MB RAM** — don't run multiple heavy processes simultaneously.
5. **Do NOT use googlevoicehat-soundcard overlay** — causes cracking. Use `max98357a` overlay instead.
6. **Toy speaker is mono** — always output mono audio (channels=1). Sending stereo to a single speaker causes crackling artifacts.
7. **Pi Zero 2W over-amplifies I2S** — use ALSA softvol to attenuate. Without it, audio is distorted.
8. **USB mic needs max capture volume** — default is too quiet. Set numid=8 to 35 and enable AGC.
9. **Card numbers change** — always verify with `aplay -l` / `arecord -l` after hardware changes.
10. **TAF-MAIN-01 is fully bypassed** — don't waste time on it.
