"""
Agente 3 - Designer
Gera backgrounds para cada slide:
1. Tenta screenshot do topagenda.online via Playwright (cache 7 dias)
2. Fallback: gradiente nas cores da marca (sem API externa)
"""
import os
import time
import uuid
import random
import shutil
from PIL import Image, ImageDraw
from config import OUTPUT_DIR, ASSETS_DIR

# Paletas de gradiente fallback (top → bottom) nas cores da marca
GRADIENT_PALETTES = [
    ((5, 30, 70), (27, 111, 187)),    # azul escuro → azul marca
    ((8, 42, 90), (15, 60, 120)),     # azul marinho → azul médio
    ((5, 30, 70), (20, 80, 50)),      # azul escuro → verde escuro
    ((10, 20, 60), (27, 111, 187)),   # quase preto → azul
    ((3, 18, 50), (8, 42, 90)),       # sólido azul muito escuro
    ((12, 35, 80), (77, 182, 72)),    # azul → verde marca
]

_SITE_CACHE = None  # caminho do cache em memória para este run


def _site_cache_path() -> str:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    return os.path.join(ASSETS_DIR, "site_bg_cache.jpg")


def _fetch_website_bg() -> str | None:
    """
    Faz screenshot de topagenda.online e cacheia por 7 dias em ASSETS_DIR.
    Retorna o caminho do cache ou None se falhar.
    """
    global _SITE_CACHE
    if _SITE_CACHE and os.path.exists(_SITE_CACHE):
        return _SITE_CACHE

    cache = _site_cache_path()

    # Cache válido por 7 dias
    if os.path.exists(cache):
        age = time.time() - os.path.getmtime(cache)
        if age < 7 * 24 * 3600:
            _SITE_CACHE = cache
            return cache

    try:
        from playwright.sync_api import sync_playwright
        print("  [Designer] Capturando background do site topagenda.online...")
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto("https://topagenda.online", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            page.screenshot(path=cache, full_page=False, type="jpeg", quality=92)
            browser.close()
        print("  [Designer] Background capturado e cacheado.")
        _SITE_CACHE = cache
        return cache
    except Exception as e:
        print(f"  [Designer] Screenshot do site falhou ({e}) — usando gradiente")
        return None


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
    Gera backgrounds para cada slide.
    Retorna lista de caminhos de arquivo.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image_paths = []
    post_id = str(uuid.uuid4())[:8]

    # Tenta screenshot do site (compartilhado por todos os slides do post)
    site_bg = _fetch_website_bg()

    slides = script.get("slides", [])
    for slide in slides:
        slide_num = slide.get("slide_number", 1)
        filename = f"{post_id}_slide{slide_num}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if site_bg:
            shutil.copy(site_bg, filepath)
            print(f"  [Designer] Bg site → {filename}")
        else:
            palette = random.choice(GRADIENT_PALETTES)
            img = _make_gradient(1080, 1080, palette[0], palette[1])
            img.save(filepath, "PNG")
            print(f"  [Designer] Bg gradiente → {filename}")

        image_paths.append(filepath)

    return image_paths
