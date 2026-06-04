# Build it yourself

## Prerequisites

- Raspberry Pi Zero 2 W (or any Pi with GPIO)
- MAX98357A I2S amplifier connected to a speaker
- [PicoClaw](https://github.com/sipeed/picoclaw) installed
- ElevenLabs API key ([elevenlabs.io](https://elevenlabs.io))

## Install

```bash
git clone https://github.com/manaporkun/talking-flower.git
cd talking-flower
chmod +x scripts/*.sh
./scripts/setup.sh
```

## Configure

```bash
cd voice-assistant
cp .env.example .env
nano .env
```

## Set up the character

```bash
cp character/SOUL.md ~/.picoclaw/workspace/
cp character/IDENTITY.md ~/.picoclaw/workspace/
cp character/AGENTS.md ~/.picoclaw/workspace/
cp character/USER.md.example ~/.picoclaw/workspace/USER.md
nano ~/.picoclaw/workspace/USER.md
```

## Run

```bash
picoclaw gateway &
./scripts/start.sh
```

## Run on boot

```bash
sudo cp systemd/picoclaw-gateway.service /etc/systemd/system/
sudo cp systemd/talking-flower.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable picoclaw-gateway talking-flower
sudo systemctl start picoclaw-gateway talking-flower
```

## Deploying changes

```bash
# On the Pi
cd ~/talking-flower
bash deploy.sh
```

Pulls latest from git and syncs character files to PicoClaw's workspace. Character changes take effect immediately. If `voice_assistant.py` changed, restart the service: `sudo systemctl restart talking-flower`.

## Customizing the character

Personality lives in four Markdown files in PicoClaw's workspace:

| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, voice rules, audio tags |
| `IDENTITY.md` | Name, description, purpose |
| `AGENTS.md` | Direct behavioral instructions |
| `USER.md` | Info about the user |

Edit these to make any character — a pirate, a robot, a grumpy cat. The ElevenLabs v3 audio tags work with any voice.

## Configuration

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
