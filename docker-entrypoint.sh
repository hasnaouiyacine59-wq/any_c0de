#!/bin/bash
set -e

# start tor
tor -f /etc/tor/torrc &
TOR_PID=$!

# start virtual display — 24-bit, 96 DPI
Xvfb :99 -screen 0 1920x1080x24 -dpi 96 &
export DISPLAY=:99

# start fluxbox — suppress config warnings
mkdir -p ~/.fluxbox
fluxbox 2>/dev/null &
sleep 1

# set GTK theme to fix ActiveText color detection
export GTK_THEME=Adwaita:dark
export GTK2_RC_FILES=/dev/null

# start VNC + noVNC
x11vnc -display :99 -nopw -forever -shared -quiet -rfbport 5900 &
websockify --web /usr/share/novnc 6080 localhost:5900 &

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  noVNC ready → http://localhost:6080     ║"
echo "  ║  Open: http://localhost:6080/vnc.html    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# wait for Tor to bootstrap (100%)
echo "  [~] Waiting for Tor to bootstrap..."
for i in $(seq 1 60); do
    STATUS=$(curl -s --socks5 127.0.0.1:9050 --max-time 5 http://check.torproject.org/api/ip 2>/dev/null | grep -o '"IsTor":true' || true)
    if [ -n "$STATUS" ]; then
        echo "  [✓] Tor ready"
        break
    fi
    sleep 3
done

# run session
exec python3 jdid.py "$@"
