#!/bin/bash
set -e

# start tor
tor -f /etc/tor/torrc &
sleep 3

# start virtual display — 24-bit, 96 DPI
Xvfb :99 -screen 0 1920x1080x24 -dpi 96 &
export DISPLAY=:99

# start fluxbox with a dark theme to fix ActiveText color detection
fluxbox &
sleep 1

# set GTK theme to avoid headless color detection (ActiveText = rgb(255,0,0) in headless)
export GTK_THEME=Adwaita:dark
export GTK2_RC_FILES=/dev/null

# start VNC server (no password)
x11vnc -display :99 -nopw -forever -shared -quiet -rfbport 5900 &

# start noVNC websocket proxy → web access on port 6080
websockify --web /usr/share/novnc 6080 localhost:5900 &

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  noVNC ready → http://localhost:6080     ║"
echo "  ║  Open: http://localhost:6080/vnc.html    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# run session
exec python3 jdid.py "$@"
