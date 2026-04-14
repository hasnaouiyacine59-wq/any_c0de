FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb x11-utils \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 \
    libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m camoufox fetch

COPY . .

CMD ["bash", "-c", "rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp & until xdpyinfo -display :99 >/dev/null 2>&1; do sleep 0.5; done && DISPLAY=:99 python cum.py"]
