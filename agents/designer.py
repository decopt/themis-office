"""
Agente 3 - Designer
Gera backgrounds gradient para cada slide usando Pillow.
Sem chamadas de API externas — totalmente gratuito.
"""
import os
import uuid
import random
from PIL import Image, ImageDraw
from config import OUTPUT_DIR

# Paletas de gradiente (top → bottom) nas cores da marca
GRADIENT_PALETTES = [
    ((5, 30, 70), (27, 111, 187)),    # azul escuro → azul marca
    ((8, 42, 90), (15, 60, 120)),     # azul marinho → azul médio
    ((5, 30, 70), (20, 80, 50)),      # azul escuro → verde escuro
    ((10, 20, 60), (27, 111, 187)),   # quase preto → azul
    ((3, 18, 50), (8, 42, 90)),       # sólido azul muito escuro
    ((12, 35, 80), (77, 182, 72)),    # azul → verde marca
]


def _make_gradient(width: int, height: int, color_top: tuple, color_bottom: tuple) -> Image.Image:
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / height
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def run(script: dict, strategy: dict) -> list:
    """
    Gera imagens de background gradient para cada slide.
    Retorna lista de caminhos de arquivo.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image_paths = []
    post_id = str(uuid.uuid4())[:8]

    slides = script.get("slides", [])
    for slide in slides:
        slide_num = slide.get("slide_number", 1)
        palette = random.choice(GRADIENT_PALETTES)
        img = _make_gradient(1080, 1080, palette[0], palette[1])

        filename = f"{post_id}_slide{slide_num}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath, "PNG")
        image_paths.append(filepath)
        print(f"  [Designer] Background gerado: {filename}")

    return image_paths
