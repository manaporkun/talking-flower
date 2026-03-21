# Talking Flower

Turn a Nintendo Talking Flower toy into an AI-powered voice assistant using a Raspberry Pi Zero 2 W and [PicoClaw](https://github.com/sipeed/picoclaw).

Press the button on the flower, say something, and it responds with a personality-rich voice — powered by an LLM with a Talking Flower character from Super Mario Bros. Wonder.

## How It Works

```
Button press → Record audio → Speech-to-text → LLM (via PicoClaw) → Text-to-speech → Speaker
```

1. **Press the physical button** on the flower (or Space key for dev)
2. **Speak** — recording auto-stops when you stop talking (voice activity detection)
3. **Transcription** via ElevenLabs Scribe or OpenAI Whisper
4. **LLM response** through PicoClaw (supports any model — Kimi, GPT, Claude, etc.)
5. **Text-to-speech** via ElevenLabs v3 with emotional audio tags
6. **Audio playback** through the flower's speaker

The flower has a character: **Flowey**, a cheerful, sassy Talking Flower who gasps at everything, whispers secrets, and makes flower puns. The character is defined in PicoClaw's persona files and can be fully customized.

## Features

- **Voice activity detection** — auto-stops recording when you stop speaking
- **Sentence-pipelined TTS** — first sentence plays while the rest generate
- **GPIO button support** — use the toy's physical button, auto-detects GPIO
- **Audio device auto-detection** — finds USB audio by name, survives reboots
- **Startup chime** — Flowey greets you when powered on
- **Dual STT support** — ElevenLabs Scribe or OpenAI Whisper
- **Character system** — personality defined in Markdown files, easy to customize
- **ElevenLabs v3 audio tags** — `[gasps]`, `[whispers]`, `[excited]` in responses

## Quick Start

### Prerequisites

- Raspberry Pi Zero 2 W (or any Pi)
- USB sound card + microphone + speaker
- [PicoClaw](https://github.com/sipeed/picoclaw) installed
- ElevenLabs API key ([elevenlabs.io](https://elevenlabs.io))

### Install

```bash
git clone https://github.com/YOUR_USERNAME/talking-flower.git
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

## Hardware Setup

See [docs/hardware.md](docs/hardware.md) for full wiring guide.

**TL;DR:**
- Button on toy's sub-board → GPIO17 + GND via jumper wires
- Speaker wires → USB sound card headphone output (optionally through a PAM8403 amp)
- USB sound card → Pi's data micro-USB port (with OTG adapter)

## Customizing the Character

The flower's personality lives in four Markdown files in PicoClaw's workspace:

| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, voice rules, audio tag usage |
| `IDENTITY.md` | Name, description, purpose |
| `AGENTS.md` | Direct behavioral instructions |
| `USER.md` | Info about you (location, preferences) |

Edit these to create any character you want — a pirate, a robot, a grumpy cat. The ElevenLabs audio tags (`[whispers]`, `[laughs]`, etc.) work with any character.

## Project Structure

```
talking-flower/
├── README.md
├── LICENSE
├── docs/
│   └── hardware.md         # Wiring guide
├── picoclaw/
│   ├── SOUL.md              # Character personality
│   ├── IDENTITY.md          # Character identity
│   ├── AGENTS.md            # Behavioral instructions
│   └── USER.md.example      # User info template
├── voice-assistant/
│   ├── voice_assistant.py   # Main application
│   ├── .env.example         # Config template
│   └── requirements.txt
├── scripts/
│   ├── setup.sh             # Install dependencies
│   └── start.sh             # Launch everything
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
| `STARTUP_MESSAGE` | | What Flowey says on boot |

See `.env.example` for the complete list.

## License

MIT
