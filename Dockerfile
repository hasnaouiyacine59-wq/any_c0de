FROM python:3.10-slim

# system deps for Playwright + Xvfb + noVNC
RUN apt-get update && apt-get install -y \
    xvfb x11vnc fluxbox novnc websockify \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    curl wget tor \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

COPY . .

# tor config
RUN echo "SocksPort 9050\nControlPort 9051\nCookieAuthentication 0" > /etc/tor/torrc

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 6080 = noVNC web, 5900 = raw VNC
EXPOSE 6080 5900
ENTRYPOINT ["/entrypoint.sh"]
