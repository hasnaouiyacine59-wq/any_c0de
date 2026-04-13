#!/bin/bash
set -e

# start tor
tor -f /etc/tor/torrc &
sleep 3

# start virtual display — match resolution to spoofed viewport
# use 24-bit color depth, 96 DPI to match devicePixelRatio=1
Xvfb :99 -screen 0 1920x1080x24 -dpi 96 &
export DISPLAY=:99

# start fluxbox window manager
fluxbox &
sleep 1

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
