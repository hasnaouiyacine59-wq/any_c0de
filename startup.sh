#!/bin/bash
set -e

rm -rf /root/nova_din
git clone https://github.com/hasnaouiyacine59-wq/nova_din.git /root/nova_din
cd /root/nova_din

pip install -q -r requirements.txt
python -m camoufox fetch

rm -f /tmp/.X99-lock
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
until xdpyinfo -display :99 >/dev/null 2>&1; do sleep 0.5; done

DISPLAY=:99 python -u cum.py
