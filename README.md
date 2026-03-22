# Talking Flower

Turn a Nintendo Talking Flower toy into an AI-powered voice assistant using a Raspberry Pi Zero 2 W and [PicoClaw](https://github.com/sipeed/picoclaw).

Press the button on the flower, say something, and it responds with a personality-rich voice — powered by an LLM with a Talking Flower character from Super Mario Bros. Wonder.

## How It Works

```
Button press → Record (I2S mic) → STT → LLM (PicoClaw) → TTS → Speaker (I2S amp)
```

1. **Press the physical button** on the flower (or Space key for dev)
2. **Speak** — recording auto-stops when you stop talking (voice activity detection)
3. **Transcription** via ElevenLabs Scribe or OpenAI Whisper
4. **LLM response** through PicoClaw (supports any model — Kimi, GPT, Claude, etc.)
5. **Text-to-speech** via ElevenLabs v3 with emotional audio tags
6. **Audio playback** through the flower's speaker via I2S amplifier

The flower has a character: **Flowey**, a cheerful, sassy Talking Flower who gasps at everything, whispers secrets, and makes flower puns. The character is defined in PicoClaw's persona files and can be fully customized.

## Features

- **Voice activity detection** — auto-stops recording when you stop speaking
- **Sentence-pipelined TTS** — first sentence plays while the rest generate
- **GPIO button support** — use the toy's physical button, auto-detects GPIO
- **I2S audio** — digital mic + amp via GPIO, no USB sound card needed
- **Time-aware greetings** — "Good morning!" vs "Still up? Go to sleep!"
- **Idle chatter** — Flowey talks randomly when nobody's around, just like in the game
- **Dual STT support** — ElevenLabs Scribe or OpenAI Whisper
- **Character system** — personality defined in Markdown files, easy to customize
- **ElevenLabs v3 audio tags** — `[gasps]`, `[whispers]`, `[excited]` in responses
- **Auto-start on boot** — systemd services for headless operation
- **WiFi watchdog** — auto-reconnects if WiFi drops

## Hardware

| Component | Purpose |
|-----------|---------|
| Nintendo Talking Flower toy | Enclosure, button, speaker |
| Raspberry Pi Zero 2 WH | Brain |
| MAX98357A I2S amplifier | Speaker output (DAC + amp, via GPIO) |
| INMP441 I2S MEMS microphone | Voice input (via GPIO) |
| Dupont jumper wires | Connecting everything |

No USB sound card needed — all audio is digital via I2S on the GPIO header.

See [docs/hardware.md](docs/hardware.md) for the full wiring guide.

**TL;DR wiring:**
- Button → GPIO17 + GND
- MAX98357A → GPIO18, 19, 21 + 5V + GND → toy speaker
- INMP441 → GPIO18, 19, 20 + 3.3V + GND

## Quick Start

### Prerequisites

- Raspberry Pi Zero 2 W (or any Pi with GPIO)
- MAX98357A I2S amplifier + INMP441 I2S microphone
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
nano .env  # Add your API keys and preferences
```

### Copy PicoClaw Persona Files

```bash
cp picoclaw/SOUL.md ~/.picoclaw/workspace/
cp picoclaw/IDENTITY.md ~/.picoclaw/workspace/
cp picoclaw/AGENTS.md ~/.picoclaw/workspace/
cp picoclaw/USER.md.example ~/.picoclaw/workspace/USER.md
nano ~/.picoclaw/workspace/USER.md  # Personalize
```

### Run

```bash
# Start PicoClaw gateway (for Telegram integration, optional)
picoclaw gateway &

# Start the voice assistant
./scripts/start.sh
```

### Run on Boot (Optional)

```bash
sudo cp systemd/picoclaw-gateway.service /etc/systemd/system/
sudo cp systemd/talking-flower.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable picoclaw-gateway talking-flower
sudo systemctl start picoclaw-gateway talking-flower
```

## Customizing the Character

The flower's personality lives in four Markdown files in PicoClaw's workspace:

| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, voice rules, audio tag usage |
| `IDENTITY.md` | Name, description, purpose |
| `AGENTS.md` | Direct behavioral instructions |
| `USER.md` | Info about you (location, preferences) |

Edit these to create any character you want — a pirate, a robot, a grumpy cat. The ElevenLabs v3 audio tags (`[whispers]`, `[laughs]`, `[gasps]`, `[excited]`, `[sarcastic]`) work with any character.

## Project Structure

```
talking-flower/
├── README.md
├── LICENSE
├── docs/
│   └── hardware.md              # Wiring guide + BOM
├── picoclaw/
│   ├── SOUL.md                  # Character personality
│   ├── IDENTITY.md              # Character identity
│   ├── AGENTS.md                # Behavioral instructions
│   └── USER.md.example          # User info template
├── voice-assistant/
│   ├── voice_assistant.py       # Main application
│   ├── idle_chatter.py          # Random idle lines + time greetings
│   ├── .env.example             # Config template
│   └── requirements.txt
├── scripts/
│   ├── setup.sh                 # Install dependencies
│   ├── start.sh                 # Launch everything
│   ├── wifi-watchdog.sh         # Auto-reconnect WiFi
│   └── cleanup.sh               # Log rotation + session cleanup
└── systemd/
    ├── picoclaw-gateway.service
    └── talking-flower.service
```

## Configuration

All config is in `voice-assistant/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_PROVIDER` | `elevenlabs` | `elevenlabs` or `openai` |
| `ELEVENLABS_MODEL_ID` | `eleven_v3` | TTS model |
| `PICOCLAW_MODEL` | `kimi-turbo` | LLM model name in PicoClaw |
| `INPUT_MODE` | `auto` | `gpio`, `keyboard`, or `auto` |
| `GPIO_BUTTON_PIN` | `17` | GPIO pin for physical button |
| `SILENCE_DURATION` | `1.5` | Seconds of silence before auto-stop |
| `IDLE_CHATTER` | `1` | Enable random idle comments |
| `IDLE_INTERVAL_MIN` | `5` | Min minutes between idle lines |
| `IDLE_INTERVAL_MAX` | `15` | Max minutes between idle lines |
| `STARTUP_MESSAGE` | | What Flowey says on boot (or auto time-greeting) |

See `.env.example` for the complete list.

## License

MIT
