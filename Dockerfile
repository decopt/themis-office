FROM python:3.11-slim

WORKDIR /app

# Logs em tempo real (sem buffering)
ENV PYTHONUNBUFFERED=1

# Dependencias do sistema (Pillow + Noto Sans + Playwright/Chromium)
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    fonts-noto-core \
    # Dependencias do Chromium para Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala Chromium para Playwright
RUN playwright install chromium

COPY . .

# APOS o COPY . . — sobrescreve Arial do repo com NotoSans do sistema
# (NotoSans-Bold/Regular tem suporte completo a acentos do portugues)
RUN find /usr/share/fonts -name "NotoSans-Bold.ttf"    | head -1 | xargs -I{} cp {} /app/assets/font_bold.ttf && \
    find /usr/share/fonts -name "NotoSans-Regular.ttf" | head -1 | xargs -I{} cp {} /app/assets/font_regular.ttf && \
    echo "Fonts instaladas: $(ls /app/assets/*.ttf)"

RUN mkdir -p /app/output

CMD ["python", "main.py"]
