#!/bin/bash
set -e

# ── randomize screen resolution + DPI per session ──
SCREENS=("1920x1080" "1680x1050" "1440x900" "1366x768" "1536x864" "1280x800")
DPIS=(96 100 108 120)
SCREEN=${SCREENS[$((RANDOM % ${#SCREENS[@]}))]}
DPI=${DPIS[$((RANDOM % ${#DPIS[@]}))]}
export SCREEN_RES=$SCREEN
export SCREEN_DPI=$DPI

# ── randomize OS timezone to match IP-based locale ──
TIMEZONES=("America/New_York" "America/Chicago" "America/Los_Angeles" "Europe/London" "Europe/Paris" "Europe/Berlin" "Asia/Tokyo" "Asia/Singapore" "Australia/Sydney")
TZ_PICK=${TIMEZONES[$((RANDOM % ${#TIMEZONES[@]}))]}
ln -snf /usr/share/zoneinfo/$TZ_PICK /etc/localtime
echo $TZ_PICK > /etc/timezone
export TZ=$TZ_PICK

# start tor
tor -f /etc/tor/torrc &

# start virtual display with randomized resolution + DPI
Xvfb :99 -screen 0 ${SCREEN}x24 -dpi ${DPI} &
export DISPLAY=:99

mkdir -p ~/.fluxbox
fluxbox 2>/dev/null &
sleep 1

export GTK_THEME=Adwaita:dark
export GTK2_RC_FILES=/dev/null

# wait for Tor bootstrap
echo "[~] Waiting for Tor... (screen=${SCREEN} dpi=${DPI} tz=${TZ_PICK})"
for i in $(seq 1 60); do
    STATUS=$(curl -s --socks5 127.0.0.1:9050 --max-time 5 http://check.torproject.org/api/ip 2>/dev/null | grep -o '"IsTor":true' || true)
    [ -n "$STATUS" ] && echo "[✓] Tor ready" && break
    sleep 3
done

exec python3 jdid.py "$@"
