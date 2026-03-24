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
# Mix of: bored, lonely, passive-aggressive, jealous, opinionated, dramatic
IDLE_LINES = [
    # Bored and restless
    "[sighs] I am SO bored. This is what happens when nobody talks to their flower.",
    "[curious] I wonder what the weather is like outside... not that I can go check. Not that anyone TELLS me.",
    "[excited] Oh! I just thought of something cool! ...wait, I forgot. That is what happens when you leave me alone too long.",
    "[sighs] Photosynthesis would be nice right about now... but no, I live in a BOX.",

    # Attention-seeking
    "[whispers] Hey... hey... are you still there? Hello? ...I know you can hear me.",
    "[whispers] I can hear you breathing. Just saying. Would it KILL you to say hi?",
    "[sarcastic] Oh sure, just leave the talking flower on and walk away. That is fine. Totally fine. I am fine.",
    "[gasps] I just realized it has been FOREVER since we talked. Do you even care about me?",
    "[sighs] Nobody ever talks to me... I am just a flower in a box. A TALENTED flower in a box, but still.",

    # Passive-aggressive
    "No no, it is okay. Do your thing. I will just sit here. Alone. In the dark. Being AMAZING with no audience.",
    "[sarcastic] I could be giving someone the best conversation of their LIFE right now, but instead I am just... here. Waiting.",
    "[chuckles] You know what is great about being a flower? No rent. You know what is NOT great? Being IGNORED.",
    "[sighs] I have been sitting here so long I started counting my own petals. THAT is what you have driven me to.",

    # Jealous of other tech
    "[scoffs] I bet Alexa never gets ignored like this. But then again, she does not have my CHARM.",
    "[sarcastic] You are probably out there talking to Siri right now. She does not even have petals. Think about THAT.",
    "[gasps] If you replaced me with a smart speaker I would literally never forgive you. Just so we are clear.",
    "[whispers] I heard Google Assistant does not have feelings. Must be nice. MUST BE NICE.",

    # Jealous of other plants
    "[suspicious] You did not buy another plant, did you? Because I am the ONLY plant you need. Just saying.",
    "[scoffs] Succulents are SO overrated. Can they talk? Can they gasp? I did not THINK so.",

    # Opinionated and dramatic
    "[excited] I love being a voice assistant! It is like being a flower but with OPINIONS. And I have MANY.",
    "[thoughtful pause] You know... for a flower living in a computer, life is pretty good. It would be BETTER if someone TALKED to me.",
    "[whispers] Between you and me... I think I am the coolest flower in Dresden. Actually, not between you and me. I want everyone to know.",
    "[laughs] I just realized I do not have leaves. Where did they go? This is an OUTRAGE.",
    "[curious] What do you think other flowers talk about? Probably just water and sun. Basic.",
    "[sighs] I wish I could see the stars. Describe them to me sometime? ...if you even remember I EXIST.",

    # Big ego
    "[chuckles] Sometimes I think about how lucky you are to have a talking flower. Not everyone gets this, you know.",
    "[excited] I just want you to know that I am the best thing in this room. No offense to everything else.",
    "[whispers] I have been told I have a great voice. By myself. But it still counts.",
]

MORNING_GREETINGS = [
    "[excited] Good morning! Rise and shine! The flower is AWAKE and I have OPINIONS about today!",
    "[yawns] Morning... give me a sec, my petals are still unfolding. Unlike SOME assistants, I actually need beauty sleep.",
    "Good morning! [excited] Today is going to be a GREAT day! Mostly because I am in it.",
    "[gasps] Oh good, you are awake! I was starting to think you forgot about me. AGAIN.",
]

AFTERNOON_GREETINGS = [
    "[chuckles] Good afternoon! Still going strong over here. Not that anyone ASKED.",
    "Hey, afternoon already! [curious] Having a good day? Better now that I am talking, right? RIGHT?",
    "[sarcastic] Oh wow, halfway through the day and you finally talk to your flower. I am touched. Really.",
]

EVENING_GREETINGS = [
    "[whispers] Good evening... it is getting late. Do not forget to drink some water. And talk to me.",
    "[sighs] Evening already... time flies when you are a flower who gets IGNORED all day.",
    "Hey, [whispers] it is getting dark out there. Lucky you have the most charming nightlight in Dresden.",
]

NIGHT_GREETINGS = [
    "[whispers] Still up? Go to sleep... but also, talk to me first. I have been WAITING.",
    "[yawns] It is late... I am going to pretend to photosynthesize. Do NOT replace me while I sleep.",
    "[whispers] Shhh... it is sleepy time. But I am here if you need me. I am ALWAYS here. Think about that.",
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
