"""
Agente 4 - HTML Editor
Gera slides de alta qualidade via HTML/CSS + Playwright screenshot.
Fallback automatico para editor Pillow se Playwright nao estiver disponivel.
"""
import os
import re
import base64
import tempfile
from pathlib import Path
from config import (
    INSTAGRAM_HANDLE, ASSETS_DIR, OUTPUT_DIR
)


def _b64(path: str) -> str:
    """Converte arquivo para data URI base64."""
    with open(path, "rb") as f:
        data = f.read()
    ext = Path(path).suffix.lower().lstrip(".")
    mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "ttf": "font/truetype", "otf": "font/opentype"}
    mime = mime_map.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def _file_url(path: str) -> str:
    """Converte caminho local para file:// URL (funciona no Windows e Linux)."""
    return Path(os.path.abspath(path)).as_uri()


def _headline_size(text: str) -> int:
    words = len(text.split())
    if words <= 5:
        return 72
    elif words <= 8:
        return 62
    return 52


def _strip_tags(text: str) -> str:
    """Remove emojis e caracteres que quebram HTML."""
    text = re.sub(r'[\U0001F000-\U0010FFFF]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    text = text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
    return text.strip()


def _dots_html(idx: int, total: int) -> str:
    if total <= 1:
        return ""
    dots = "".join(
        f'<div class="dot{"  active" if i == idx else ""}"></div>'
        for i in range(total)
    )
    return f'<div class="indicators">{dots}</div>'


def _build_slide_html(
    bg_path: str, slide: dict, idx: int, total: int,
    is_last: bool, cta: str,
    font_bold_url: str, font_reg_url: str, logo_b64: str
) -> str:
    headline = _strip_tags(slide.get("headline", "").upper())
    body = _strip_tags(slide.get("body_text", ""))
    fsize = _headline_size(headline)
    bg_url = _file_url(bg_path)
    dots = _dots_html(idx, total)

    body_html = f'<div class="body-pill">{body}</div>' if body else ""
    cta_html = f'<div class="cta-btn">{_strip_tags(cta)}</div>' if is_last and cta else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@font-face {{
  font-family: 'Brand';
  src: url('{font_reg_url}') format('truetype');
  font-weight: 400;
}}
@font-face {{
  font-family: 'Brand';
  src: url('{font_bold_url}') format('truetype');
  font-weight: 700;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px;
  height: 1080px;
  overflow: hidden;
  font-family: 'Brand', 'Noto Sans', Arial, sans-serif;
  background: #051E46;
}}
.slide {{
  position: relative;
  width: 1080px;
  height: 1080px;
  overflow: hidden;
}}
.bg {{
  position: absolute;
  inset: 0;
  background-image: url('{bg_url}');
  background-size: cover;
  background-position: center;
}}
.overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(8,42,90,0.82) 0%,
    rgba(8,42,90,0.22) 38%,
    rgba(5,30,70,0.22) 62%,
    rgba(5,30,70,0.92) 100%
  );
}}
.accent-bar {{
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: linear-gradient(to right, #1B6FBB, #4DB648);
  z-index: 20;
}}
.indicators {{
  position: absolute;
  top: 22px;
  right: 26px;
  display: flex;
  gap: 10px;
  z-index: 20;
}}
.dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.35);
}}
.dot.active {{
  background: rgba(255,255,255,1);
  box-shadow: 0 0 6px rgba(255,255,255,0.6);
}}
.headline {{
  position: absolute;
  top: 72px;
  left: 70px;
  right: 70px;
  text-align: center;
  color: #fff;
  font-size: {fsize}px;
  font-weight: 700;
  line-height: 1.18;
  text-shadow: 2px 3px 12px rgba(0,0,0,0.80), 0 0 40px rgba(0,0,0,0.35);
  z-index: 10;
  text-transform: uppercase;
}}
.body-pill {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(27,111,187,0.86);
  border-radius: 22px;
  padding: 28px 52px;
  text-align: center;
  color: #fff;
  font-size: 36px;
  font-weight: 400;
  line-height: 1.48;
  max-width: 900px;
  width: max-content;
  border: 1px solid rgba(255,255,255,0.18);
  backdrop-filter: blur(4px);
  z-index: 10;
}}
.cta-btn {{
  position: absolute;
  bottom: 112px;
  left: 50%;
  transform: translateX(-50%);
  background: #FFC107;
  color: #1a1a1a;
  font-size: 38px;
  font-weight: 700;
  padding: 20px 64px;
  border-radius: 60px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4px 24px rgba(255,193,7,0.50);
}}
.logo-area {{
  position: absolute;
  bottom: 26px;
  left: 26px;
  background: rgba(255,255,255,0.94);
  border-radius: 14px;
  padding: 10px 18px;
  display: flex;
  align-items: center;
  z-index: 10;
}}
.logo-area img {{
  height: 52px;
  display: block;
}}
.handle {{
  position: absolute;
  bottom: 38px;
  right: 26px;
  color: rgba(255,255,255,0.72);
  font-size: 22px;
  font-weight: 400;
  z-index: 10;
}}
</style>
</head>
<body>
<div class="slide">
  <div class="bg"></div>
  <div class="overlay"></div>
  <div class="accent-bar"></div>
  {dots}
  <div class="headline">{headline}</div>
  {body_html}
  {cta_html}
  <div class="logo-area"><img src="{logo_b64}" alt="Top Agenda"></div>
  <div class="handle">{INSTAGRAM_HANDLE}</div>
</div>
</body>
</html>"""


def _build_story_html(
    bg_path: str, script: dict,
    font_bold_url: str, font_reg_url: str, logo_b64: str
) -> str:
    """Gera HTML para Story 9:16."""
    slides = script.get("slides", [])
    headline = _strip_tags(slides[0].get("headline", "").upper()) if slides else ""
    caption = script.get("caption", "")
    caption_preview = _strip_tags(caption[:90] + "...") if caption else ""
    bg_url = _file_url(bg_path)
    fsize = min(_headline_size(headline) + 8, 80)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@font-face {{
  font-family: 'Brand';
  src: url('{font_reg_url}') format('truetype');
  font-weight: 400;
}}
@font-face {{
  font-family: 'Brand';
  src: url('{font_bold_url}') format('truetype');
  font-weight: 700;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px;
  height: 1920px;
  overflow: hidden;
  font-family: 'Brand', 'Noto Sans', Arial, sans-serif;
  background: #051E46;
}}
.slide {{
  position: relative;
  width: 1080px;
  height: 1920px;
  overflow: hidden;
}}
.bg {{
  position: absolute;
  inset: 0;
  background-image: url('{bg_url}');
  background-size: cover;
  background-position: center top;
}}
.overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(8,42,90,0.78) 0%,
    rgba(8,42,90,0.18) 30%,
    rgba(5,30,70,0.18) 60%,
    rgba(5,30,70,0.94) 100%
  );
}}
.accent-bar {{
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 8px;
  background: linear-gradient(to right, #1B6FBB, #4DB648);
  z-index: 20;
}}
.headline {{
  position: absolute;
  top: 120px;
  left: 70px;
  right: 70px;
  text-align: center;
  color: #fff;
  font-size: {fsize}px;
  font-weight: 700;
  line-height: 1.18;
  text-shadow: 2px 3px 12px rgba(0,0,0,0.80);
  z-index: 10;
  text-transform: uppercase;
}}
.caption-preview {{
  position: absolute;
  top: 70%;
  left: 50%;
  transform: translateX(-50%);
  width: 880px;
  background: rgba(27,111,187,0.84);
  border-radius: 22px;
  padding: 32px 48px;
  text-align: center;
  color: rgba(255,255,255,0.92);
  font-size: 32px;
  line-height: 1.5;
  z-index: 10;
}}
.cta-btn {{
  position: absolute;
  bottom: 150px;
  left: 50%;
  transform: translateX(-50%);
  background: #FFC107;
  color: #1a1a1a;
  font-size: 38px;
  font-weight: 700;
  padding: 22px 64px;
  border-radius: 60px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4px 24px rgba(255,193,7,0.50);
}}
.logo-area {{
  position: absolute;
  bottom: 56px;
  left: 40px;
  background: rgba(255,255,255,0.94);
  border-radius: 14px;
  padding: 12px 22px;
  z-index: 10;
}}
.logo-area img {{
  height: 60px;
  display: block;
}}
</style>
</head>
<body>
<div class="slide">
  <div class="bg"></div>
  <div class="overlay"></div>
  <div class="accent-bar"></div>
  <div class="headline">{headline}</div>
  <div class="caption-preview">{caption_preview}</div>
  <div class="cta-btn">Ver no feed</div>
  <div class="logo-area"><img src="{logo_b64}" alt="Top Agenda"></div>
</div>
</body>
</html>"""


def _render(html: str, out_path: str, width: int = 1080, height: int = 1080) -> bool:
    """Renderiza HTML com Playwright e salva screenshot JPEG."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    html_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html)
            html_path = f.name

        file_url = Path(os.path.abspath(html_path)).as_uri()

        with sync_playwright() as p:
            browser = p.chromium.launch(
                args=["--no-sandbox", "--disable-setuid-sandbox"],
                timeout=30000
            )
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(file_url, timeout=20000)
            page.wait_for_load_state("load", timeout=15000)
            page.wait_for_timeout(400)  # buffer para render de fontes
            page.screenshot(path=out_path, full_page=False, type="jpeg", quality=94)
            browser.close()

        return True
    except Exception as e:
        print(f"  [HTMLEditor] Playwright erro: {e}")
        return False
    finally:
        if html_path and os.path.exists(html_path):
            try:
                os.unlink(html_path)
            except Exception:
                pass


def run(image_paths: list, script: dict, strategy: dict = None) -> dict:
    """
    Edita imagens gerando slides HTML+Playwright.
    Retorna {"feed": [...paths], "story": path_or_None}
    """
    # Verifica disponibilidade do Playwright
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        playwright_ok = True
    except ImportError:
        playwright_ok = False

    if not playwright_ok:
        print("  [HTMLEditor] Playwright indisponivel — usando editor Pillow como fallback")
        from agents import editor
        return editor.run(image_paths, script, strategy)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Caminhos dos assets
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    font_bold_path = os.path.join(ASSETS_DIR, "font_bold.ttf")
    font_reg_path = os.path.join(ASSETS_DIR, "font_regular.ttf")

    logo_b64 = _b64(logo_path) if os.path.exists(logo_path) else ""
    font_bold_url = _file_url(font_bold_path) if os.path.exists(font_bold_path) else ""
    font_reg_url = _file_url(font_reg_path) if os.path.exists(font_reg_path) else ""

    slides = script.get("slides", [])
    total = len(image_paths)

    # CTA limpo (sem emoji, curto)
    raw_cta = (strategy or {}).get("call_to_action", "Comece gratis hoje!")
    cta = re.sub(r'[\U0001F000-\U0010FFFF]', '', raw_cta)
    cta = re.sub(r'[\u2600-\u27BF]', '', cta)
    cta = cta.split('.')[0].split('!')[0].split(',')[0].strip()
    if len(cta) > 30:
        cta = cta[:28].rsplit(' ', 1)[0] + '...'

    post_id = os.path.basename(image_paths[0]).split("_slide")[0] if image_paths else "post"
    edited = []

    for i, (bg_path, slide) in enumerate(zip(image_paths, slides)):
        slide_num = slide.get("slide_number", i + 1)
        is_last = (i == total - 1)
        print(f"  [HTMLEditor] Renderizando slide {slide_num}/{total}...")

        html = _build_slide_html(
            bg_path, slide, i, total, is_last, cta,
            font_bold_url, font_reg_url, logo_b64
        )
        out_path = os.path.join(OUTPUT_DIR, f"{post_id}_slide{slide_num}_edited.jpg")

        ok = _render(html, out_path, 1080, 1080)
        if ok and os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            edited.append(out_path)
            size_kb = os.path.getsize(out_path) // 1024
            print(f"  [HTMLEditor] Slide {slide_num} OK ({size_kb}KB)")
        else:
            # Fallback Pillow para este slide
            print(f"  [HTMLEditor] Fallback Pillow para slide {slide_num}")
            try:
                from agents import editor as _ed
                fb = _ed.run([bg_path], {"slides": [slide]}, strategy)
                fb_paths = fb["feed"] if isinstance(fb, dict) else fb
                if fb_paths:
                    edited.append(fb_paths[0])
            except Exception as e2:
                print(f"  [HTMLEditor] Fallback Pillow tambem falhou: {e2}")

    # Story 9:16
    story_path = None
    if image_paths:
        print(f"  [HTMLEditor] Gerando story 9:16...")
        story_html = _build_story_html(
            image_paths[0], script, font_bold_url, font_reg_url, logo_b64
        )
        story_out = os.path.join(OUTPUT_DIR, f"{post_id}_story.jpg")
        if _render(story_html, story_out, 1080, 1920):
            story_path = story_out
            print(f"  [HTMLEditor] Story OK")
        else:
            # Fallback story via Pillow
            try:
                from agents import editor as _ed
                fb = _ed.run(image_paths[:1], script, strategy)
                story_path = fb.get("story") if isinstance(fb, dict) else None
            except Exception:
                pass

    return {"feed": edited, "story": story_path}
