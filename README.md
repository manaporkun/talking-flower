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

### Teardown

The toy has two PCBs connected by a 6-wire ribbon cable: a main board (TAF-MAIN-01) with the original processor, and a sub-board (TAF-SUB-01) with the button and speaker. The main board is bypassed entirely.

<p align="center">
  <img src="docs/images/main-board-side-a.jpg" alt="Original main board — discarded" width="400">
  <img src="docs/images/sub-board-button-speaker.jpg" alt="Sub board with button contacts and speaker pads" width="400">
</p>

### Mapping the wires

The ribbon cable had six wires with no documentation. I desoldered it from the main board and used a multimeter to figure out what each one did:

| Wire | Function | How I figured it out |
|------|----------|----------------------|
| Black + White | Button (two sides) | Continuity across the dome switch contacts |
| Purple + Gray | Speaker | Resistance read 7–16Ω, matching an 8Ω speaker coil |
| Blue | Battery (likely) | Process of elimination — not button, not speaker |

Then Dupont wires were soldered directly to the sub-board pads in place of the ribbon cable.

<p align="center">
  <img src="docs/images/sub-board-soldered.jpg" alt="Sub board with Dupont wires soldered" width="400">
</p>

### Assembly

- **Button**: Black wire → GPIO17, White wire → GND (with internal pull-up). Pressing the dome bridges them, pulling GPIO17 low.
- **Speaker**: MAX98357A I2S amplifier (mounted on a Google AIY VoiceHAT) drives the toy's original 8Ω speaker through the sub-board traces.
- **Mic**: USB C-Media mic for now. An INMP441 I2S MEMS mic is planned and will free up the USB port.

<p align="center">
  <img src="docs/images/flower-wiring-back.jpg" alt="Final wiring inside the flower" width="400">
</p>

Full pin map, ALSA configuration, and the multimeter mapping notes: [docs/hardware.md](docs/hardware.md).

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

### Prerequisites

- Raspberry Pi Zero 2 W (or any Pi with GPIO)
- MAX98357A I2S amplifier connected to a speaker
- [PicoClaw](https://github.com/sipeed/picoclaw) installed
- ElevenLabs API key ([elevenlabs.io](https://elevenlabs.io))

### Install

```bash
git clone https://github.com/manaporkun/talking-flower.git
cd talking-flower
chmod +x scripts/*.sh
./scripts/setup.sh
```

### Configure

```bash
cd voice-assistant
cp .env.example .env
nano .env
```

### Set up the character

```bash
cp character/SOUL.md ~/.picoclaw/workspace/
cp character/IDENTITY.md ~/.picoclaw/workspace/
cp character/AGENTS.md ~/.picoclaw/workspace/
cp character/USER.md.example ~/.picoclaw/workspace/USER.md
nano ~/.picoclaw/workspace/USER.md
```

### Run

```bash
picoclaw gateway &
./scripts/start.sh
```

### Run on boot

```bash
sudo cp systemd/picoclaw-gateway.service /etc/systemd/system/
sudo cp systemd/talking-flower.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable picoclaw-gateway talking-flower
sudo systemctl start picoclaw-gateway talking-flower
```

### Deploying changes

```bash
# On the Pi
cd ~/talking-flower
bash deploy.sh
```

Pulls latest from git and syncs character files to PicoClaw's workspace. Character changes take effect immediately. If `voice_assistant.py` changed, restart the service: `sudo systemctl restart talking-flower`.

### Customizing the character

Personality lives in four Markdown files in PicoClaw's workspace:

| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, voice rules, audio tags |
| `IDENTITY.md` | Name, description, purpose |
| `AGENTS.md` | Direct behavioral instructions |
| `USER.md` | Info about the user |

Edit these to make any character — a pirate, a robot, a grumpy cat. The ElevenLabs v3 audio tags work with any voice.

### Configuration

All config in `voice-assistant/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_PROVIDER` | `elevenlabs` | `elevenlabs` or `openai` |
| `ELEVENLABS_MODEL_ID` | `eleven_v3` | TTS model |
| `PICOCLAW_MODEL` | `kimi-turbo` | LLM model |
| `INPUT_MODE` | `auto` | `gpio`, `keyboard`, or `auto` |
| `GPIO_BUTTON_PIN` | `17` | GPIO pin for the button |
| `SILENCE_DURATION` | `1.5` | Seconds of silence before auto-stop |
| `IDLE_CHATTER` | `1` | Enable random idle comments |
| `STARTUP_MESSAGE` | | What Flowey says on boot |

See `.env.example` for the full list.

## Project structure

```
talking-flower/
├── voice-assistant/         # Main application
├── character/               # Personality files (SOUL, IDENTITY, AGENTS, USER)
├── scripts/                 # setup, start, wifi-watchdog, cleanup
├── systemd/                 # Boot services
├── docs/                    # Hardware guide + build photos
└── deploy.sh                # Pull latest + sync to Pi
```

## Related

This project contributed an [ElevenLabs TTS skill](https://github.com/sipeed/picoclaw/pull/1905) upstream to PicoClaw, enabling any PicoClaw agent to use ElevenLabs text-to-speech.

## License

MIT
