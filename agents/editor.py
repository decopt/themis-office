"""
Agente 4 - Editor
Monta posts no estilo do banner Top Agenda:
foto de fundo + overlay escuro degradê + texto branco bold + logo.
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import (
    BRAND_PRIMARY_COLOR, BRAND_GREEN_COLOR,
    BRAND_SECONDARY_COLOR, BRAND_ACCENT_COLOR,
    PRODUCT_NAME, INSTAGRAM_HANDLE, ASSETS_DIR, OUTPUT_DIR
)

SLIDE_SIZE   = (1080, 1080)
STORY_SIZE   = (1080, 1920)
FONT_BOLD    = os.path.join(ASSETS_DIR, "font_bold.ttf")
FONT_REGULAR = os.path.join(ASSETS_DIR, "font_regular.ttf")
LOGO_PATH    = os.path.join(ASSETS_DIR, "logo.png")


def _strip_emoji(text: str) -> str:
    """Remove emojis e normaliza caracteres Unicode (NFC) para evitar tofu em acentos."""
    import unicodedata
    # Normaliza para NFC (forma composta) — corrige acentos decompostos (NFD)
    text = unicodedata.normalize("NFC", text)
    # Substitui variantes tipográficas por equivalentes simples
    replacements = {
        '\u2018': "'", '\u2019': "'",   # aspas simples curvas
        '\u201C': '"', '\u201D': '"',   # aspas duplas curvas
        '\u2013': '-', '\u2014': '-',   # en-dash, em-dash
        '\u2026': '...', '\u2022': '-', # reticências, bullet
        '\u2192': '->', '\u2190': '<-', # setas
        '\u00D7': 'x', '\u00F7': '/',  # × ÷
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Remove emojis (U+1F000 em diante) e símbolos decorativos raros
    text = re.sub(r'[\U0001F000-\U0010FFFF]', '', text)
    # Remove símbolos miscelâneos (U+2600-U+27BF) que costumam ser emojis
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    return text.strip()


def _font(size: int, bold: bool = False):
    try:
        path = FONT_BOLD if bold else FONT_REGULAR
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default(size=size)


def _wrap(text: str, font, max_w: int, draw) -> list:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _add_gradient_overlay(img: Image.Image, size: tuple) -> Image.Image:
    """Overlay escuro degradê — mais escuro em cima e embaixo, mais claro no meio."""
    w, h = size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Gradiente de cima (para headline) — azul escuro da marca
    for y in range(h // 2):
        alpha = int(185 * (1 - y / (h / 2)))
        draw.line([(0, y), (w, y)], fill=(8, 42, 90, alpha))

    # Gradiente de baixo (para branding) — azul mais profundo da marca
    for y in range(h // 2, h):
        alpha = int(210 * ((y - h // 2) / (h / 2)))
        draw.line([(0, y), (w, y)], fill=(5, 30, 70, alpha))

    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _add_logo(img: Image.Image, size: tuple, corner: str = "bottomleft") -> Image.Image:
    """Cola o logo com fundo branco arredondado no canto."""
    if not os.path.exists(LOGO_PATH):
        return img
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = int(size[1] * 0.09)
        ratio  = logo_h / logo.height
        logo_w = int(logo.width * ratio)
        logo   = logo.resize((logo_w, logo_h), Image.LANCZOS)

        pad = 18
        # Fundo branco pill
        bg = Image.new("RGBA", (logo_w + pad * 2, logo_h + pad), (255, 255, 255, 230))
        bg_r = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw_bg = ImageDraw.Draw(bg_r)
        draw_bg.rounded_rectangle([(0, 0), bg.size], radius=14, fill=(255, 255, 255, 220))
        bg_r.paste(logo, (pad, pad // 2), logo)

        margin = 28
        if corner == "bottomleft":
            x = margin
            y = size[1] - bg.height - margin
        else:
            x = size[0] - bg.width - margin
            y = size[1] - bg.height - margin

        img.paste(bg_r, (x, y), bg_r)
    except Exception as e:
        print(f"  [Editor] Logo error: {e}")
    return img


def _draw_headline(draw, img, text: str, size: tuple, font_size: int = 68):
    """Headline branco bold no topo com sombra."""
    text = _strip_emoji(text)
    font = _font(font_size, bold=True)
    max_w = int(size[0] * 0.85)
    lines = _wrap(text, font, max_w, draw)

    pad_top = int(size[1] * 0.07)
    y = pad_top
    for line in lines[:4]:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = (size[0] - lw) // 2
        # Sombra
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 160))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += (bbox[3] - bbox[1]) + 12


def _draw_body(draw, img: Image.Image, text: str, size: tuple):
    """Texto de corpo centralizado com pill colorido."""
    if not text:
        return
    text = _strip_emoji(text)
    font = _font(34)
    max_w = int(size[0] * 0.78)
    lines = _wrap(text, font, max_w, draw)

    pill_h = len(lines) * 48 + 28
    pill_w = max_w + 48
    pill_x = (size[0] - pill_w) // 2
    pill_y = (size[1] - pill_h) // 2 - 20

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=16,
        fill=(*BRAND_PRIMARY_COLOR, 200)
    )
    img.alpha_composite(overlay)
    draw = ImageDraw.Draw(img)

    y = pill_y + 14
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (size[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += 48


def _draw_cta_button(draw, text: str, size: tuple):
    """Botão CTA amarelo no rodapé (estilo banner)."""
    text = _strip_emoji(text)
    # Garante que o texto cabe no botão (máx 32 chars)
    if len(text) > 32:
        text = text[:30].rsplit(' ', 1)[0] + '...'
    font = _font(36, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    btn_w = (bbox[2] - bbox[0]) + 64
    btn_h = 58
    btn_x = (size[0] - btn_w) // 2
    btn_y = int(size[1] * 0.82)

    draw.rounded_rectangle(
        [(btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h)],
        radius=30,
        fill=BRAND_ACCENT_COLOR
    )
    tx = btn_x + (btn_w - (bbox[2] - bbox[0])) // 2
    ty = btn_y + (btn_h - (bbox[3] - bbox[1])) // 2
    draw.text((tx + 1, ty + 1), text, font=font, fill=(0, 0, 0, 80))
    draw.text((tx, ty), text, font=font, fill=(30, 30, 30, 255))


def _draw_slide_indicator(draw, idx: int, total: int, size: tuple):
    """Bolinhas de progresso no topo direito."""
    if total <= 1:
        return
    r, gap, y = 5, 14, 24
    total_w = total * (r * 2) + (total - 1) * gap
    x = size[0] - total_w - 24
    for i in range(total):
        color = (255, 255, 255, 255) if i == idx else (255, 255, 255, 90)
        draw.ellipse([(x, y), (x + r * 2, y + r * 2)], fill=color)
        x += r * 2 + gap


def _process_slide(image_path: str, slide: dict, idx: int, total: int,
                   is_last: bool, cta: str, size=SLIDE_SIZE) -> str:
    img = Image.open(image_path).convert("RGBA").resize(size, Image.LANCZOS)

    # Leve blur no fundo para destacar texto
    bg = img.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.alpha_composite(bg.convert("RGBA"), img.split()[3].convert("RGBA"))
    img = Image.open(image_path).convert("RGBA").resize(size, Image.LANCZOS)

    img = _add_gradient_overlay(img, size)
    draw = ImageDraw.Draw(img)

    headline = slide.get("headline", "")
    body     = slide.get("body_text", "")

    if headline:
        _draw_headline(draw, img, headline.upper(), size)

    if body:
        _draw_body(draw, img, body, size)

    if is_last and cta:
        _draw_cta_button(draw, cta, size)

    _draw_slide_indicator(draw, idx, total, size)
    _add_logo(img, size, "bottomleft")

    out_path = image_path.replace(".png", "_edited.jpg")
    img.convert("RGB").save(out_path, "JPEG", quality=94)
    return out_path


def _make_story(feed_images: list, script: dict, post_id: str) -> str:
    """Gera imagem de Story 9:16 a partir do primeiro slide do feed."""
    if not feed_images:
        return None
    try:
        img = Image.open(feed_images[0]).convert("RGBA").resize(STORY_SIZE, Image.LANCZOS)
        img = _add_gradient_overlay(img, STORY_SIZE)
        draw = ImageDraw.Draw(img)

        # Headline
        headline = script["slides"][0].get("headline", "") if script.get("slides") else ""
        if headline:
            _draw_headline(draw, img, headline.upper(), STORY_SIZE, font_size=72)

        # Swipe up / CTA
        cta = script.get("caption", "")[:60] + "..."
        font_cta = _font(30)
        lines = _wrap(cta, font_cta, int(STORY_SIZE[0] * 0.8), draw)
        y = int(STORY_SIZE[1] * 0.72)
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font_cta)
            x = (STORY_SIZE[0] - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, font=font_cta, fill=(255, 255, 255, 200))
            y += 42

        _draw_cta_button(draw, "Ver no feed →", STORY_SIZE)
        _add_logo(img, STORY_SIZE, "bottomleft")

        story_path = os.path.join(OUTPUT_DIR, f"{post_id}_story.jpg")
        img.convert("RGB").save(story_path, "JPEG", quality=94)
        return story_path
    except Exception as e:
        print(f"  [Editor] Erro ao criar story: {e}")
        return None


def run(image_paths: list, script: dict, strategy: dict = None) -> dict:
    """
    Edita todas as imagens e gera o story.
    Retorna {"feed": [...paths], "story": path_or_None}
    """
    slides = script.get("slides", [])
    total  = len(image_paths)
    edited = []
    # CTA vem da estratégia (curto, sem emoji) — fallback genérico
    raw_cta = (strategy or {}).get("call_to_action", "Experimente gratis hoje!")
    # Pega só a primeira frase curta do CTA, máx 28 chars
    cta = _strip_emoji(raw_cta)
    cta = cta.split('.')[0].split('!')[0].split(',')[0].strip()
    if len(cta) > 28:
        cta = cta[:26].rsplit(' ', 1)[0] + '...'

    for i, (path, slide) in enumerate(zip(image_paths, slides)):
        print(f"  [Editor] Editando slide {i+1}/{total}...")
        try:
            out = _process_slide(path, slide, i, total, i == total - 1, cta)
            edited.append(out)
        except Exception as e:
            print(f"  [Editor] ERRO slide {i+1}: {e}")
            edited.append(path)

    # Extrai post_id do nome do arquivo
    post_id = os.path.basename(image_paths[0]).split("_slide")[0] if image_paths else "story"
    story_path = _make_story(image_paths, script, post_id)
    if story_path:
        print(f"  [Editor] Story gerado: {os.path.basename(story_path)}")

    return {"feed": edited, "story": story_path}
