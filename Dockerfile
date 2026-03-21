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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# APOS o COPY . . — sobrescreve Arial do repo com NotoSans do sistema
# (NotoSans-Bold/Regular tem suporte completo a acentos do portugues)
RUN find /usr/share/fonts -name "NotoSans-Bold.ttf"    | head -1 | xargs -I{} cp {} /app/assets/font_bold.ttf && \
    find /usr/share/fonts -name "NotoSans-Regular.ttf" | head -1 | xargs -I{} cp {} /app/assets/font_regular.ttf && \
    echo "Fonts instaladas: $(ls /app/assets/*.ttf)"

RUN mkdir -p /app/output

CMD ["python", "main.py"]
