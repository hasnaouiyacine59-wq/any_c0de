#!/bin/bash
set -e

# start tor
tor -f /etc/tor/torrc &

# start virtual display
Xvfb :99 -screen 0 1920x1080x24 -dpi 96 &
export DISPLAY=:99

mkdir -p ~/.fluxbox
fluxbox 2>/dev/null &
sleep 1

export GTK_THEME=Adwaita:dark
export GTK2_RC_FILES=/dev/null

# wait for Tor bootstrap
echo "[~] Waiting for Tor..."
for i in $(seq 1 60); do
    STATUS=$(curl -s --socks5 127.0.0.1:9050 --max-time 5 http://check.torproject.org/api/ip 2>/dev/null | grep -o '"IsTor":true' || true)
    [ -n "$STATUS" ] && echo "[✓] Tor ready" && break
    sleep 3
done

exec python3 jdid.py "$@"
