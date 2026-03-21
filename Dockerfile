FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (Pillow + Noto Sans com suporte completo ao português)
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

# Copia Noto Sans (suporte completo a português e Unicode) para assets
RUN mkdir -p /app/assets && \
    find /usr/share/fonts -name "NotoSans-Bold.ttf"    | head -1 | xargs -I{} cp {} /app/assets/font_bold.ttf && \
    find /usr/share/fonts -name "NotoSans-Regular.ttf" | head -1 | xargs -I{} cp {} /app/assets/font_regular.ttf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/output

CMD ["python", "main.py"]
