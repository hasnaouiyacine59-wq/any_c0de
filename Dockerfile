FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 \
    libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m camoufox fetch

COPY . .

CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & sleep 1 && DISPLAY=:99 python cum.py"]
