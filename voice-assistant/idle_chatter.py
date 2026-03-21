"""Flowey idle chatter — random comments every few minutes, time-aware greetings."""

import json
import os
import random
import time
from datetime import datetime
from pathlib import Path

CHATTER_DIR = Path(__file__).parent / "chatter_cache"
CHATTER_DIR.mkdir(exist_ok=True)

# Flowey-style idle lines — pre-written so no LLM call needed
IDLE_LINES = [
    "[sighs] Nobody ever talks to me... I am just a flower in a box.",
    "[whispers] Hey... hey... are you still there?",
    "[curious] I wonder what the weather is like outside... not that I can go check.",
    "[excited] Oh! I just thought of something cool! ...wait, I forgot.",
    "[chuckles] You know what is great about being a flower? No rent.",
    "[sighs] Photosynthesis would be nice right about now...",
    "[whispers] I can hear you breathing. Just saying.",
    "[gasps] Did I ever tell you that sunflowers can grow up to twelve feet tall? That is HUGE!",
    "[sarcastic] Oh sure, just leave the talking flower on. That is fine. I will just... be here.",
    "[excited] I love being a voice assistant! It is like being a flower but with OPINIONS!",
    "[thoughtful pause] You know... for a flower living in a computer, life is pretty good.",
    "[whispers] Between you and me... I think I am the coolest flower in Dresden.",
    "[laughs] I just realized I do not have leaves. Where did they go?",
    "[curious] What do you think other flowers talk about? Probably just water and sun. Boring.",
    "[sighs] I wish I could see the stars. Describe them to me sometime?",
]

MORNING_GREETINGS = [
    "[excited] Good morning! Rise and shine! The flower is AWAKE!",
    "[yawns] Morning... give me a sec, my petals are still unfolding.",
    "Good morning! [excited] Today is going to be a GREAT day, I can feel it in my roots!",
]

AFTERNOON_GREETINGS = [
    "[chuckles] Good afternoon! Still going strong over here.",
    "Hey, afternoon already! [curious] Having a good day so far?",
]

EVENING_GREETINGS = [
    "[whispers] Good evening... it is getting late. Do not forget to drink some water.",
    "[sighs] Evening already... time flies when you are a flower.",
    "Hey, [whispers] it is getting dark out there. Cozy in here though.",
]

NIGHT_GREETINGS = [
    "[whispers] Still up? Go to sleep... even flowers need rest.",
    "[yawns] It is late... I am going to pretend to photosynthesize. Good night.",
    "[whispers] Shhh... it is sleepy time. But I am here if you need me.",
]


def get_time_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return random.choice(MORNING_GREETINGS)
    elif 12 <= hour < 17:
        return random.choice(AFTERNOON_GREETINGS)
    elif 17 <= hour < 22:
        return random.choice(EVENING_GREETINGS)
    else:
        return random.choice(NIGHT_GREETINGS)


def get_idle_line():
    return random.choice(IDLE_LINES)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "greeting":
        print(get_time_greeting())
    else:
        print(get_idle_line())
