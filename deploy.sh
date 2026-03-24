#!/bin/bash
# Deploy script — pull latest from git and sync to picoclaw workspace
set -e

REPO_DIR=~/talking-flower
WORKSPACE=~/.picoclaw/workspace
SKILL_DIR=$WORKSPACE/skills/flowey-telegram-voice

echo "Pulling latest from git..."
cd $REPO_DIR
git pull --ff-only

echo "Syncing character files..."
cp $REPO_DIR/character/SOUL.md $WORKSPACE/SOUL.md
cp $REPO_DIR/character/AGENTS.md $WORKSPACE/AGENTS.md
cp $REPO_DIR/character/IDENTITY.md $WORKSPACE/IDENTITY.md
[ -f $REPO_DIR/character/USER.md ] && cp $REPO_DIR/character/USER.md $WORKSPACE/USER.md

echo "Syncing idle chatter module..."
cp $REPO_DIR/voice-assistant/idle_chatter.py $SKILL_DIR/idle_chatter.py 2>/dev/null || true

echo "Done! Restart voice-assistant to apply changes."
echo "  sudo systemctl restart voice-assistant"
