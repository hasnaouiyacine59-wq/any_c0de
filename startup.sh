#!/bin/bash
set -e

rm -rf /root/nova_din
git clone https://github.com/hasnaouiyacine59-wq/nova_din.git /root/nova_din
cd /root/nova_din

pip install -q -r requirements.txt
python -c "
from camoufox.pkgman import get_path
import os, subprocess, sys
if os.path.exists(get_path()):
    print('camoufox already installed, skipping fetch')
else:
    subprocess.run([sys.executable, '-m', 'camoufox', 'fetch'], check=True)
"

rm -f /tmp/.X99-lock
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
until xdpyinfo -display :99 >/dev/null 2>&1; do sleep 0.5; done

DISPLAY=:99 python -u cum.py
