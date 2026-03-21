#!/usr/bin/env bash
# WiFi watchdog — restarts wlan0 if connectivity is lost
# Run via cron: */2 * * * * /home/plue/talking-flower/scripts/wifi-watchdog.sh

PING_TARGET="1.1.1.1"
LOG="/tmp/wifi-watchdog.log"

if ! ping -c 1 -W 5 "$PING_TARGET" > /dev/null 2>&1; then
    echo "$(date): WiFi down, restarting wlan0..." >> "$LOG"
    sudo ip link set wlan0 down
    sleep 2
    sudo ip link set wlan0 up
    sleep 5
    if ping -c 1 -W 5 "$PING_TARGET" > /dev/null 2>&1; then
        echo "$(date): WiFi restored." >> "$LOG"
    else
        echo "$(date): WiFi still down after restart." >> "$LOG"
    fi
fi
