# The Build

How a Nintendo Talking Flower toy was gutted and rebuilt around a Raspberry Pi Zero 2 W.

## Teardown

The toy has two PCBs connected by a 6-wire ribbon cable: a main board (TAF-MAIN-01) with the original processor, and a sub-board (TAF-SUB-01) with the button and speaker. The main board is bypassed entirely.

<p align="center">
  <img src="images/main-board-side-a.jpg" alt="Original main board — discarded" width="400">
  <img src="images/sub-board-button-speaker.jpg" alt="Sub board with button contacts and speaker pads" width="400">
</p>

## Mapping the wires

The ribbon cable had six wires with no documentation. I desoldered it from the main board and used a multimeter to figure out what each one did:

| Wire | Function | How I figured it out |
|------|----------|----------------------|
| Black + White | Button (two sides) | Continuity across the dome switch contacts |
| Purple + Gray | Speaker | Resistance read 7–16Ω, matching an 8Ω speaker coil |
| Blue | Battery (likely) | Process of elimination — not button, not speaker |

Then Dupont wires were soldered directly to the sub-board pads in place of the ribbon cable.

<p align="center">
  <img src="images/sub-board-soldered.jpg" alt="Sub board with Dupont wires soldered" width="400">
</p>

## Assembly

- **Button**: Black wire → GPIO17, White wire → GND (with internal pull-up). Pressing the dome bridges them, pulling GPIO17 low.
- **Speaker**: MAX98357A I2S amplifier (mounted on a Google AIY VoiceHAT) drives the toy's original 8Ω speaker through the sub-board traces.
- **Mic**: USB C-Media mic for now. An INMP441 I2S MEMS mic is planned and will free up the USB port.

<p align="center">
  <img src="images/flower-wiring-back.jpg" alt="Final wiring inside the flower" width="400">
</p>

Full pin map, ALSA configuration, and the multimeter mapping notes: [hardware.md](hardware.md).
