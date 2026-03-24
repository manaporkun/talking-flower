#!/usr/bin/env python3
"""Talking Flower Voice Assistant — press a button, talk, get a response."""

import os
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

# --- Config ---

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")
ELEVENLABS_STT_MODEL = os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
OPENAI_TRANSCRIBE_LANGUAGE = os.getenv("OPENAI_TRANSCRIBE_LANGUAGE", "en")

STT_PROVIDER = os.getenv("STT_PROVIDER", "elevenlabs")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
INPUT_DEVICE_HINT = os.getenv("INPUT_DEVICE_HINT", "USB")
OUTPUT_DEVICE_HINT = os.getenv("OUTPUT_DEVICE_HINT", "USB")

PICOCLAW_BIN = os.getenv("PICOCLAW_BIN", "/home/plue/picoclaw")
PICOCLAW_MODEL = os.getenv("PICOCLAW_MODEL", "kimi-turbo")
PICOCLAW_SESSION = os.getenv("PICOCLAW_SESSION", "voice:assistant")

SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.015"))
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "1.5"))
MIN_SPEECH_DURATION = float(os.getenv("MIN_SPEECH_DURATION", "0.5"))
MAX_RECORD_SECONDS = float(os.getenv("MAX_RECORD_SECONDS", "30"))

GPIO_BUTTON_PIN = int(os.getenv("GPIO_BUTTON_PIN", "17"))
INPUT_MODE = os.getenv("INPUT_MODE", "auto")  # "gpio", "keyboard", or "auto"
STARTUP_MESSAGE = os.getenv("STARTUP_MESSAGE", "")
IDLE_CHATTER = os.getenv("IDLE_CHATTER", "1").lower() not in ("0", "false", "no", "off")
IDLE_INTERVAL_MIN = int(os.getenv("IDLE_INTERVAL_MIN", "5"))
IDLE_INTERVAL_MAX = int(os.getenv("IDLE_INTERVAL_MAX", "15"))

HOLD_THRESHOLD = float(os.getenv("HOLD_THRESHOLD", "0.3"))
TAP_WINDOW = float(os.getenv("TAP_WINDOW", "0.4"))
QUIPS_DIR = Path(os.getenv("QUIPS_DIR", str(Path.home() / ".picoclaw/workspace/skills/flowey-telegram-voice/quips_wav")))
INDICATORS_DIR = Path(os.getenv("INDICATORS_DIR", str(Path.home() / ".picoclaw/workspace/skills/flowey-telegram-voice/indicators_wav")))

INPUT_FALLBACK_RATES = [16000, 48000, 44100, 32000, 8000]


# --- Audio Device Detection ---

def find_alsa_device_by_hint(hint):
    """Find ALSA plughw device string by name hint. Survives reboots."""
    try:
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "card" in line and hint.lower() in line.lower():
                card = line.split("card ")[1].split(":")[0].strip()
                return f"plughw:{card},0"
    except Exception:
        pass
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "card" in line and hint.lower() in line.lower():
                card = line.split("card ")[1].split(":")[0].strip()
                return f"plughw:{card},0"
    except Exception:
        pass
    return None


def resolve_output_device():
    """Find the ALSA output device by hint, falling back to default."""
    dev = find_alsa_device_by_hint(OUTPUT_DEVICE_HINT)
    if dev:
        return dev
    return os.getenv("OUTPUT_DEVICE", "default")


def resolve_input_device():
    """Find sounddevice input index by hint."""
    devices = sd.query_devices()
    needle = INPUT_DEVICE_HINT.lower()
    for i, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0 and needle in dev["name"].lower():
            return i, dev["name"]
    for i, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            return i, dev["name"]
    raise RuntimeError("No input audio device found")


def find_working_rate(device_idx):
    for rate in INPUT_FALLBACK_RATES:
        try:
            test = sd.InputStream(device=device_idx, samplerate=rate,
                                  channels=1, dtype="float32")
            test.close()
            return rate
        except Exception:
            continue
    raise RuntimeError("No supported sample rate found")


OUTPUT_DEVICE = resolve_output_device()


# --- Recording ---

def record_until_silence(device_idx, rate):
    """Record audio, auto-stop after silence following speech."""
    q = queue.Queue()
    frames = []
    speech_detected = False
    silence_start = None

    def callback(indata, frame_count, time_info, status):
        q.put(indata.copy())

    stream = sd.InputStream(device=device_idx, samplerate=rate,
                            channels=1, dtype="float32", callback=callback)
    stream.start()

    start_time = time.monotonic()
    chunk_samples = int(rate * 0.1)
    buf = np.array([], dtype=np.float32)

    try:
        while True:
            if time.monotonic() - start_time > MAX_RECORD_SECONDS:
                print(f"\r\033[K Max duration reached.", flush=True)
                break

            try:
                chunk = q.get(timeout=0.05)
                frames.append(chunk)
                buf = np.concatenate([buf, chunk.squeeze()])
            except queue.Empty:
                continue

            while buf.size >= chunk_samples:
                segment = buf[:chunk_samples]
                buf = buf[chunk_samples:]
                rms = float(np.sqrt(np.mean(np.square(segment))))

                if rms > SILENCE_THRESHOLD:
                    speech_detected = True
                    silence_start = None
                    bar = "#" * min(40, int(rms * 400))
                    print(f"\r\033[K [{bar:<40}]", end="", flush=True)
                elif speech_detected:
                    if silence_start is None:
                        silence_start = time.monotonic()
                    elif time.monotonic() - silence_start >= SILENCE_DURATION:
                        print(f"\r\033[K Processing...", flush=True)
                        while not q.empty():
                            frames.append(q.get_nowait())
                        stream.stop()
                        stream.close()
                        if not frames:
                            return np.array([], dtype=np.float32), rate
                        audio = np.concatenate(frames, axis=0).squeeze()
                        trim = int(SILENCE_DURATION * rate)
                        if audio.size > trim:
                            audio = audio[:-trim]
                        return audio, rate
                else:
                    print(f"\r\033[K Listening...", end="", flush=True)

    except KeyboardInterrupt:
        pass

    stream.stop()
    stream.close()
    while not q.empty():
        frames.append(q.get_nowait())
    if not frames:
        return np.array([], dtype=np.float32), rate
    return np.concatenate(frames, axis=0).squeeze(), rate


# --- Audio Helpers ---

def resample(audio, src_rate, dst_rate):
    if src_rate == dst_rate or audio.size == 0:
        return audio
    duration = audio.shape[0] / float(src_rate)
    dst_len = max(1, int(round(duration * dst_rate)))
    src_x = np.linspace(0, duration, num=audio.shape[0], endpoint=False)
    dst_x = np.linspace(0, duration, num=dst_len, endpoint=False)
    return np.interp(dst_x, src_x, audio).astype(np.float32)


def save_wav(path, audio, rate):
    audio16 = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio16.tobytes())


# --- STT ---

def transcribe_elevenlabs(wav_path):
    with open(wav_path, "rb") as f:
        r = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            files={"file": (Path(wav_path).name, f, "audio/wav")},
            data={"model_id": ELEVENLABS_STT_MODEL, "language_code": "en"},
            timeout=120,
        )
    if not r.ok:
        raise RuntimeError(f"ElevenLabs STT: {r.status_code} {r.text}")
    return r.json().get("text", "").strip()


def transcribe_openai(wav_path):
    with open(wav_path, "rb") as f:
        data = {"model": OPENAI_TRANSCRIBE_MODEL}
        if OPENAI_TRANSCRIBE_LANGUAGE:
            data["language"] = OPENAI_TRANSCRIBE_LANGUAGE
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"file": (Path(wav_path).name, f, "audio/wav")},
            data=data, timeout=120,
        )
    if not r.ok:
        raise RuntimeError(f"OpenAI STT: {r.status_code} {r.text}")
    return r.json().get("text", "").strip()


def transcribe(wav_path):
    if STT_PROVIDER == "elevenlabs":
        return transcribe_elevenlabs(wav_path)
    return transcribe_openai(wav_path)


# --- LLM ---

def ask_picoclaw(message):
    result = subprocess.run(
        [PICOCLAW_BIN, "agent", "-m", message,
         "--model", PICOCLAW_MODEL, "-s", PICOCLAW_SESSION],
        capture_output=True, text=True, timeout=120,
    )
    output = result.stdout + result.stderr
    lines = output.split("\n")
    collecting = False
    response_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("\U0001f99e"):
            collecting = True
            first = stripped.lstrip("\U0001f99e").strip()
            if first:
                response_lines.append(first)
            continue
        if collecting:
            response_lines.append(line)
    if response_lines:
        return "\n".join(response_lines).strip()
    for line in lines:
        if "Response:" in line:
            idx = line.index("Response:") + len("Response:")
            return line[idx:].strip()
    return output.strip().split("\n")[-1] if output.strip() else "[no response]"


# --- TTS ---

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    for part in parts:
        clean = re.sub(r'\*\*|__|\*|_|#{1,6}\s*|`{1,3}', '', part.strip())
        clean = re.sub(r'^\s*[-*]\s+', '', clean).strip()
        if not clean:
            continue
        if chunks and len(chunks[-1]) < 40:
            chunks[-1] += " " + clean
        else:
            chunks.append(clean)
    return chunks if chunks else [text.strip()]


def tts_chunk(text):
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": ELEVENLABS_MODEL_ID,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=120,
    )
    if not r.ok:
        raise RuntimeError(f"ElevenLabs TTS: {r.status_code} {r.text}")
    return r.content


def play_audio_file(path):
    if shutil.which("mpg123") and path.endswith(".mp3"):
        subprocess.run(["mpg123", "-q", "-a", OUTPUT_DEVICE, path])
    elif shutil.which("aplay"):
        wav_path = path.replace(".mp3", ".wav")
        if path.endswith(".mp3") and shutil.which("ffmpeg"):
            subprocess.run(["ffmpeg", "-y", "-i", path, wav_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            path = wav_path
        subprocess.run(["aplay", "-D", OUTPUT_DEVICE, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("ffplay"):
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path])


def speak_and_play(text):
    chunks = split_sentences(text)

    if len(chunks) == 1:
        mp3_data = tts_chunk(chunks[0])
        with open("response_0.mp3", "wb") as f:
            f.write(mp3_data)
        play_audio_file("response_0.mp3")
        return

    audio_queue = queue.Queue()
    gen_done = threading.Event()

    def generate_worker():
        for i, chunk in enumerate(chunks):
            try:
                mp3_data = tts_chunk(chunk)
                path = f"response_{i}.mp3"
                with open(path, "wb") as f:
                    f.write(mp3_data)
                audio_queue.put(path)
            except Exception as e:
                print(f"\n  TTS error on chunk {i}: {e}", flush=True)
        gen_done.set()

    threading.Thread(target=generate_worker, daemon=True).start()

    while True:
        try:
            play_audio_file(audio_queue.get(timeout=0.1))
        except queue.Empty:
            if gen_done.is_set() and audio_queue.empty():
                break


def speak(text):
    """Convenience: TTS and play a single string."""
    mp3_data = tts_chunk(text)
    with open("speak_tmp.mp3", "wb") as f:
        f.write(mp3_data)
    play_audio_file("speak_tmp.mp3")


# --- Idle Chatter ---

def get_idle_line():
    """Get a random idle chatter line."""
    try:
        from idle_chatter import get_idle_line as _get
        return _get()
    except ImportError:
        return None


def get_time_greeting():
    """Get a time-aware greeting."""
    try:
        from idle_chatter import get_time_greeting as _get
        return _get()
    except ImportError:
        return None


class IdleChatterTimer:
    """Speaks random lines when idle. Resets on any interaction."""

    def __init__(self, speak_fn):
        self._speak = speak_fn
        self._stop = threading.Event()
        self._reset = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def reset(self):
        self._reset.set()

    def stop(self):
        self._stop.set()

    def _loop(self):
        import random
        while not self._stop.is_set():
            wait = random.randint(IDLE_INTERVAL_MIN * 60, IDLE_INTERVAL_MAX * 60)
            # Wait, but break early if reset or stopped
            for _ in range(wait):
                if self._stop.is_set():
                    return
                if self._reset.is_set():
                    self._reset.clear()
                    break
                time.sleep(1)
            else:
                # Timer expired without reset — say something
                line = get_idle_line()
                if line:
                    try:
                        self._speak(line)
                    except Exception:
                        pass


# --- Button Sounds ---

def play_random_sound(directory):
    """Play a random WAV from a directory."""
    import glob as _glob
    sounds = _glob.glob(str(Path(directory) / "*.wav"))
    if sounds:
        play_audio_file(random.choice(sounds))


def play_indicator(name):
    """Play a named indicator sound (e.g. 'chatter_on', 'memory_cleared')."""
    path = INDICATORS_DIR / f"{name}.wav"
    if path.exists():
        play_audio_file(str(path))


# --- Conversation Turn ---

def handle_turn(dev_idx, rate):
    """One full conversation turn: record → transcribe → LLM → speak."""
    audio, actual_rate = record_until_silence(dev_idx, rate)

    if audio.size == 0:
        print(" No audio captured.")
        return

    duration = audio.size / actual_rate
    peak = float(np.max(np.abs(audio)))
    print(f" Captured {duration:.1f}s (peak={peak:.3f})")

    if duration < MIN_SPEECH_DURATION:
        print(" Too short, skipping.")
        return
    if peak < 0.01:
        print(" Too quiet, skipping.")
        return

    if actual_rate != SAMPLE_RATE:
        audio = resample(audio, actual_rate, SAMPLE_RATE)
    save_wav("last_input.wav", audio, SAMPLE_RATE)

    print(" Transcribing...", end=" ", flush=True)
    try:
        text = transcribe("last_input.wav")
    except Exception as e:
        print(f"error: {e}")
        return
    print(f'You: "{text}"')

    if not text or len(text) < 2:
        print(" Empty transcript, skipping.")
        return

    print(" Thinking...", end=" ", flush=True)
    try:
        reply = ask_picoclaw(text)
    except Exception as e:
        print(f"error: {e}")
        return
    print(f'Flowey: "{reply}"')

    if not reply or reply == "[no response]":
        print(" No response.")
        return

    print(" Speaking...", flush=True)
    try:
        speak_and_play(reply)
    except Exception as e:
        print(f" TTS error: {e}")


# --- Input Modes ---

def count_taps(button):
    """After a tap is detected, count additional taps within TAP_WINDOW."""
    taps = 1
    deadline = time.monotonic() + TAP_WINDOW
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        if button.wait_for_press(timeout=remaining):
            button.wait_for_release()
            taps += 1
            deadline = time.monotonic() + TAP_WINDOW
        else:
            break
    return taps


def run_gpio_mode(dev_idx, rate):
    """Use a physical button on GPIO with multi-press gestures.

    Hold:        Push-to-talk recording
    Single tap:  Play random Flowey quip
    Double tap:  Toggle idle chatter on/off
    Triple tap:  Clear conversation memory (new session)
    """
    from gpiozero import Button as GPIOButton

    button = GPIOButton(GPIO_BUTTON_PIN, pull_up=True, bounce_time=0.05)
    print(f"GPIO mode: pin {GPIO_BUTTON_PIN}")
    print(f"  Hold=speak | Tap=quip | 2x=toggle chatter | 3x=reset memory\n")

    session = PICOCLAW_SESSION
    idle_chatter_on = IDLE_CHATTER

    # Time-aware startup greeting
    greeting = STARTUP_MESSAGE or get_time_greeting()
    if greeting:
        try:
            speak(greeting)
        except Exception as e:
            print(f"Startup speak error: {e}")

    # Start idle chatter
    chatter = None
    if idle_chatter_on:
        chatter = IdleChatterTimer(speak)
        chatter.start()

    print("Ready.")

    while True:
        try:
            button.wait_for_press()
        except KeyboardInterrupt:
            if chatter:
                chatter.stop()
            print("\nBye!")
            return

        press_time = time.monotonic()
        button.wait_for_release()
        hold_duration = time.monotonic() - press_time

        if chatter:
            chatter.reset()

        if hold_duration < HOLD_THRESHOLD:
            # --- Tap gesture ---
            taps = count_taps(button)

            if taps == 1:
                print(" Tap — quip")
                play_random_sound(QUIPS_DIR)
            elif taps == 2:
                idle_chatter_on = not idle_chatter_on
                state = "ON" if idle_chatter_on else "OFF"
                print(f" Double-tap — idle chatter {state}")
                if idle_chatter_on:
                    if not chatter:
                        chatter = IdleChatterTimer(speak)
                    chatter.start()
                else:
                    if chatter:
                        chatter.stop()
                        chatter = None
                play_indicator("chatter_on" if idle_chatter_on else "chatter_off")
            elif taps >= 3:
                session = f"voice:{int(time.time())}"
                print(f" Triple-tap — memory cleared (new session: {session})")
                play_indicator("memory_cleared")
            continue

        # --- PTT hold — record and process ---
        # Recording already missed (we waited for release), so re-record
        # Actually: for the local version with VAD, just run a normal turn
        print("\n--- Recording ---")
        handle_turn(dev_idx, rate)
        print("\nReady.")


def run_keyboard_mode(dev_idx, rate):
    """Use Space key to trigger recording (for development/testing)."""
    import termios
    import tty

    print("Keyboard mode: press SPACE to talk, 'q' to quit.\n")

    # Time-aware startup greeting
    greeting = STARTUP_MESSAGE or get_time_greeting()
    if greeting:
        try:
            speak(greeting)
        except Exception as e:
            print(f"Startup speak error: {e}")

    # Start idle chatter
    chatter = None
    if IDLE_CHATTER:
        chatter = IdleChatterTimer(speak)
        chatter.start()

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())

        while True:
            key = sys.stdin.read(1)
            if key in ('q', 'Q', '\x03'):
                break
            if key == ' ':
                if chatter:
                    chatter.reset()
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                handle_turn(dev_idx, rate)
                print("\n[SPACE] to speak, [q] to quit\n")
                tty.setraw(sys.stdin.fileno())
    except KeyboardInterrupt:
        pass
    finally:
        if chatter:
            chatter.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\nBye!")


def has_gpio():
    """Check if we're running on a Pi with GPIO available."""
    try:
        from gpiozero import Button as GPIOButton
        GPIOButton(GPIO_BUTTON_PIN, pull_up=True).close()
        return True
    except Exception:
        return False


# --- Main ---

def main():
    dev_idx, dev_name = resolve_input_device()
    rate = find_working_rate(dev_idx)

    print("=== Talking Flower Voice Assistant ===")
    print(f"Input:  {dev_name} ({rate}Hz)")
    print(f"Output: {OUTPUT_DEVICE}")
    print(f"Model:  {PICOCLAW_MODEL}")
    print(f"STT:    {STT_PROVIDER} ({ELEVENLABS_STT_MODEL if STT_PROVIDER == 'elevenlabs' else OPENAI_TRANSCRIBE_MODEL})")
    print(f"TTS:    {ELEVENLABS_MODEL_ID}")
    print()

    if INPUT_MODE == "gpio":
        run_gpio_mode(dev_idx, rate)
    elif INPUT_MODE == "keyboard":
        run_keyboard_mode(dev_idx, rate)
    else:  # auto
        if has_gpio():
            print("GPIO detected, using button input.")
            run_gpio_mode(dev_idx, rate)
        else:
            print("No GPIO, using keyboard input.")
            run_keyboard_mode(dev_idx, rate)


if __name__ == "__main__":
    main()
