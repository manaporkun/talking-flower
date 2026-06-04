# Talking Flower

**My first hardware project — learning to solder by gutting a Nintendo toy and putting an AI inside it.**

A Talking Flower from Super Mario Bros. Wonder, rebuilt around a Raspberry Pi Zero 2 W. Press the button, talk, get a response — in character as a sassy, jealous, attention-hungry flower with opinions.

<p align="center">
  <a href="https://youtu.be/njyr6QNPWzk">
    <img src="docs/images/front.png" alt="Watch the demo" width="400">
  </a>
  <br>
  <em><a href="https://youtu.be/njyr6QNPWzk">Watch the demo on YouTube</a></em>
</p>

## Why I built this

I wanted to learn to solder and start doing hardware. Picking a Nintendo Talking Flower toy gave me a target with real constraints: an enclosure I had to fit inside, a button I had to wire to a GPIO pin, a speaker I had to drive cleanly through an I2S amp, a ribbon cable I had to figure out. All I needed to add was a brain.

By the end I had desoldered a ribbon cable, mapped six unknown wires with a multimeter, wired an I2S amplifier, and tuned an ALSA stack to stop the audio from popping — none of which I knew how to do when I started.

## What I learned

**Hardware:**
- The "button" on cheap toys isn't a tactile switch. It's a pair of contact pads bridged by a conductive rubber dome in the housing — you wire it as a normal momentary-to-ground.
- A multimeter is the bridge between "I have no idea what this wire does" and "I know exactly what this wire does." Continuity mode finds connections; resistance mode confirms speakers (an 8Ω coil reads 7–16Ω).
- Speaker wires don't always go where they look like they go. On this toy, the speaker pads route through the ribbon cable back to the main board, so desoldering the ribbon kills the speaker until you wire it back.
- Pre-soldered headers (Pi Zero 2 WH) save you from soldering 40 pins as your first project. Worth the small premium.

**Audio is the hard part:**
- The Pi Zero 2W over-amplifies I2S output. Without an ALSA `softvol` layer between the app and the amp, everything clips.
- Sending stereo to a single mono speaker causes crackling artifacts. Force `channels=1` in dmix.
- Class-D amps like the MAX98357A pop when they power on and off. A background silence stream keeps the I2S clock alive so the amp never sleeps.
- USB mics default to ~half capture volume with AGC off. Both need to be cranked, then persisted with `alsactl store`.
- `dtoverlay=googlevoicehat-soundcard` will fight you with its own codec layer. Use `dtoverlay=max98357a` even on a VoiceHAT — the VoiceHAT is just a MAX98357A in a fancier package.

**Software, briefly:**
- Push-to-talk is more reliable than wake words on a Pi Zero 2W with 416 MB of RAM.
- Pipelined TTS — synthesize sentence 2 while sentence 1 plays — is the difference between "the flower is talking" and "the flower is buffering."
- ElevenLabs v3 audio tags (`[gasps]`, `[whispers]`, `[excited]`) carry more character than any amount of prompt engineering.

## The Build

How the toy was gutted and rebuilt — teardown, multimeter wire mapping, and assembly: [docs/build.md](docs/build.md).

Full pin map, ALSA configuration, and bill of materials: [docs/hardware.md](docs/hardware.md).

## How it works

```
Button press → Record audio → Speech-to-Text → LLM → Text-to-Speech → Speaker
```

1. Press the physical button — recording starts and auto-stops when you stop speaking (RMS-based VAD).
2. Audio goes to ElevenLabs Scribe for transcription.
3. The transcript goes to an LLM via [PicoClaw](https://github.com/sipeed/picoclaw), which handles the character persona and tool access.
4. The response is synthesized with ElevenLabs v3 (with audio tags like `[gasps]`, `[whispers]`, `[excited]`).
5. Sentences play through the toy's speaker as they generate — the first one starts while the rest are still synthesizing.

The character is **Flowey**: a sassy, opinionated little flower with a diva streak. It gasps at everything, gets jealous of Alexa, guilt-trips you when ignored, and makes flower puns. Conversation history persists across reboots — Flowey remembers what you told it yesterday.

## One button, four tricks

The toy's original dome switch is the only input:

| Gesture | What happens |
|---------|--------------|
| **Hold** | Push-to-talk — speak, release, get a response |
| **Tap** | Random one-liner ("You poked me!", "Boing!", "That tickles!") |
| **Double tap** | Toggle idle chatter on/off |
| **Triple tap** | Clear conversation memory |

Plus idle chatter (Flowey says something on its own every 5–15 minutes, just like in the game) and time-aware greetings on boot.

## Hardware

| Component | Purpose |
|-----------|---------|
| Nintendo Talking Flower toy | Enclosure, button, speaker |
| Raspberry Pi Zero 2 WH | Compute |
| MAX98357A I2S amplifier | Speaker output |
| Google AIY VoiceHAT v1 | Convenient MAX98357A breakout |
| USB C-Media mic (temporary) | Voice input — INMP441 planned |

Full bill of materials, wiring diagrams, and audio tuning notes: [docs/hardware.md](docs/hardware.md).

## Build it yourself

Prerequisites, install, character setup, running on boot, deploy, and the full config reference: [docs/setup.md](docs/setup.md).

## Project structure

```
talking-flower/
├── voice-assistant/         # Main application
├── character/               # Personality files (SOUL, IDENTITY, AGENTS, USER)
├── scripts/                 # setup, start, wifi-watchdog, cleanup
├── systemd/                 # Boot services
├── docs/                    # Build story, setup guide, hardware guide, photos
└── deploy.sh                # Pull latest + sync to Pi
```

## Related

This project contributed an [ElevenLabs TTS skill](https://github.com/sipeed/picoclaw/pull/1905) upstream to PicoClaw, enabling any PicoClaw agent to use ElevenLabs text-to-speech.

## License

MIT
