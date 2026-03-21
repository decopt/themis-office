"""
Gerador de Criativos Promocionais - Top Agenda
Cores reais do site: roxo escuro + verde neon + branco
  1. Clientes/Empresas  → criativo_clientes.png
  2. Revendedores       → criativo_revendedores.png
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE        = os.path.dirname(__file__)
ASSETS_DIR  = os.path.join(BASE, "assets")
REF_DIR     = os.path.join(BASE, "referencia")
OUTPUT_DIR  = os.path.join(BASE, "output")
LOGO_PATH   = os.path.join(ASSETS_DIR, "logo.png")
PHONE_PATH  = os.path.join(REF_DIR, "phone_mockup.png")

# Fontes do sistema Windows
FONTS = {
    "black":   r"C:\Windows\Fonts\ariblk.ttf",
    "bold":    r"C:\Windows\Fonts\arialbd.ttf",
    "regular": r"C:\Windows\Fonts\arial.ttf",
}

# ─── Cores reais do Top Agenda (igual ao site) ──────────────────────────────
PURPLE_DEEP  = (18,  10, 50)     # fundo escuro
PURPLE_MID   = (45,  27, 105)    # roxo médio
PURPLE_HERO  = (72,  44, 160)    # roxo hero do site
GREEN_NEON   = (34, 197, 94)     # verde CTA do site
GREEN_DARK   = (16,  90, 40)
WHITE        = (255, 255, 255)
YELLOW       = (255, 215,  0)
BLACK        = (0,   0,   0)
GRAY_SOFT    = (180, 180, 210)

SIZE = (1080, 1080)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def fnt(size: int, style: str = "regular"):
    path = FONTS.get(style, FONTS["regular"])
    try:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default(size=size)


def gradient_v(img, top, bottom):
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def overlay_rect(img, x1, y1, x2, y2, fill_rgba, radius=0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if radius:
        d.rounded_rectangle([(x1, y1), (x2, y2)], radius=radius, fill=fill_rgba)
    else:
        d.rectangle([(x1, y1), (x2, y2)], fill=fill_rgba)
    img.alpha_composite(layer)


def text_center(draw, text, f, y, W, fill, shadow_fill=(0, 0, 0, 100)):
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    x  = (W - tw) // 2
    if shadow_fill:
        draw.text((x + 2, y + 2), text, font=f, fill=shadow_fill)
    draw.text((x, y), text, font=f, fill=fill)
    return bb[3] - bb[1]   # height


def text_height(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]


def wrap(text, f, max_w, draw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=f)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def multiline_center(draw, lines, f, y, W, fill, gap=8, shadow=True):
    for line in lines:
        h = text_center(draw, line, f, y, W, fill,
                        shadow_fill=(0, 0, 0, 120) if shadow else None)
        y += h + gap
    return y


def pill_button(img, draw, text, f, y, W, bg, text_color, pad_x=60, pad_y=18):
    bb    = draw.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    bx     = (W - bw) // 2
    overlay_rect(img, bx, y, bx + bw, y + bh, (*bg, 255), radius=bh // 2)
    draw   = ImageDraw.Draw(img)
    tx     = bx + (bw - tw) // 2
    ty     = y  + (bh - th) // 2
    draw.text((tx + 1, ty + 1), text, font=f, fill=(0, 0, 0, 80))
    draw.text((tx, ty), text, font=f, fill=text_color)
    return y + bh


def paste_logo(img, logo_h, cx, cy):
    """Cola logo centrado em (cx, cy) com pill branco semitransparente atrás."""
    try:
        logo   = Image.open(LOGO_PATH).convert("RGBA")
        ratio  = logo_h / logo.height
        logo_w = int(logo.width * ratio)
        logo   = logo.resize((logo_w, logo_h), Image.LANCZOS)
        pad    = 14
        # Pill de fundo
        px1, py1 = cx - logo_w // 2 - pad, cy - logo_h // 2 - pad // 2
        px2, py2 = cx + logo_w // 2 + pad, cy + logo_h // 2 + pad // 2
        overlay_rect(img, px1, py1, px2, py2, (255, 255, 255, 220),
                     radius=min(logo_h, 18))
        lx = cx - logo_w // 2
        ly = cy - logo_h // 2
        img.paste(logo, (lx, ly), logo)
        return logo_w, logo_h
    except Exception as e:
        print(f"  Logo err: {e}")
        return 0, 0


def paste_phone(img, target_h, x, y):
    """Cola o mockup do celular."""
    try:
        phone = Image.open(PHONE_PATH).convert("RGBA")
        ratio  = target_h / phone.height
        pw     = int(phone.width * ratio)
        phone  = phone.resize((pw, target_h), Image.LANCZOS)
        img.paste(phone, (x, y), phone)
        return pw
    except Exception as e:
        print(f"  Phone err: {e}")
        return 0


def divider(img, y, W, color, alpha=60, margin=80):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line([(margin, y), (W - margin, y)], fill=(*color, alpha), width=2)
    img.alpha_composite(layer)


def bullet_row(img, draw, icon, text, fi, ft, x, y, dot_color):
    """Bolinha colorida + texto."""
    r = 20
    overlay_rect(img, x, y, x + r * 2, y + r * 2,
                 (*dot_color, 220), radius=r)
    draw = ImageDraw.Draw(img)
    ib   = draw.textbbox((0, 0), icon, font=fi)
    iw, ih = ib[2] - ib[0], ib[3] - ib[1]
    draw.text((x + r - iw // 2, y + r - ih // 2), icon, font=fi, fill=WHITE)
    tb = draw.textbbox((0, 0), text, font=ft)
    th = tb[3] - tb[1]
    draw.text((x + r * 2 + 16, y + r - th // 2), text, font=ft, fill=WHITE)
    return y + r * 2 + 16


# ═══════════════════════════════════════════════════════════════════════════
# CRIATIVO 1 — CLIENTES / EMPRESAS
# Layout: fundo roxo | logo topo | mockup celular direita | copy esquerda
# ═══════════════════════════════════════════════════════════════════════════

def criativo_clientes():
    W, H = SIZE
    img  = Image.new("RGBA", SIZE)
    gradient_v(img, PURPLE_DEEP, (30, 15, 80))

    # Glow sutil no topo direito
    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    gd.ellipse([(600, -200), (1300, 500)], fill=(*PURPLE_HERO, 60))
    img.alpha_composite(glow)

    # Faixa verde no topo
    overlay_rect(img, 0, 0, W, 7, (*GREEN_NEON, 255))

    draw = ImageDraw.Draw(img)

    # ── Logo ─────────────────────────────────────────────────────────────
    paste_logo(img, 80, W // 2, 58)

    # ── Tag badge ─────────────────────────────────────────────────────────
    tag_f   = fnt(20, "bold")
    tag_txt = "SISTEMA DE AGENDAMENTO ONLINE"
    overlay_rect(img, 240, 112, 840, 144, (*PURPLE_MID, 180), radius=14)
    draw = ImageDraw.Draw(img)
    text_center(draw, tag_txt, tag_f, 117, W, (*GREEN_NEON,), shadow_fill=None)

    # ── Mockup celular (direita, alinhado verticalmente ao centro) ────────
    phone_h = 580
    phone_w = paste_phone(img, phone_h, 570, 155)

    # ── Copy (lado esquerdo) ───────────────────────────────────────────────
    left_max = 520
    margin_l = 54

    # Headline grande
    h1f = fnt(64, "black")
    h1  = ["Sistema de", "Agendamento", "Online"]
    y   = 168
    for line in h1:
        draw = ImageDraw.Draw(img)
        bb   = draw.textbbox((0, 0), line, font=h1f)
        tw   = bb[2] - bb[0]
        draw.text((margin_l + 2, y + 2), line, font=h1f, fill=(0, 0, 0, 120))
        draw.text((margin_l, y), line, font=h1f, fill=WHITE)
        # Sublinhado verde na ultima linha
        if line == h1[-1]:
            overlay_rect(img, margin_l, y + (bb[3] - bb[1]) + 4,
                         margin_l + tw, y + (bb[3] - bb[1]) + 9,
                         (*GREEN_NEON, 255))
        y += (bb[3] - bb[1]) + 8

    y += 18

    # Subtítulo
    sub_f   = fnt(26, "regular")
    sub_txt = "Seus clientes agendam 24h por dia,\nsem precisar ligar ou mensagem."
    draw    = ImageDraw.Draw(img)
    for line in sub_txt.split("\n"):
        h = text_height(draw, line, sub_f)
        draw.text((margin_l, y), line, font=sub_f, fill=(*GRAY_SOFT,))
        y += h + 6
    y += 20

    # Bullets / features
    fi     = fnt(15, "bold")
    fb     = fnt(25, "bold")
    feats  = [
        ("✓", "Agendamento 24h sem ligar"),
        ("✓", "Confirmacao pelo WhatsApp"),
        ("✓", "Painel de controle completo"),
        ("✓", "Teste gratis 14 dias"),
    ]
    for icon, text in feats:
        y = bullet_row(img, ImageDraw.Draw(img), icon, text,
                       fi, fb, margin_l, y, GREEN_NEON)
        draw = ImageDraw.Draw(img)
    y += 14

    # Divisor horizontal
    divider(img, y, W, WHITE, alpha=40, margin=54)
    y += 28

    # ── CTA Button (esquerda, mas largo) ──────────────────────────────────
    cta_f = fnt(34, "black")
    pill_button(img, ImageDraw.Draw(img),
                "  Experimente GRATIS  ", cta_f,
                y, W, GREEN_NEON, BLACK, pad_x=48, pad_y=16)
    draw = ImageDraw.Draw(img)

    # ── URL rodape ────────────────────────────────────────────────────────
    url_f = fnt(21, "regular")
    text_center(draw, "topagenda.online", url_f, H - 44, W,
                (*GRAY_SOFT, 180), shadow_fill=None)

    out = os.path.join(OUTPUT_DIR, "criativo_clientes.png")
    img.convert("RGB").save(out, "PNG")
    print(f"[OK] Clientes: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# CRIATIVO 2 — REVENDEDORES  (design premium SaaS, sem mockup)
# ═══════════════════════════════════════════════════════════════════════════

def _draw_circle_decoration(img, cx, cy, radius, color_rgba):
    """Circulo vazio (outline) decorativo."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)],
              outline=color_rgba, width=1)
    img.alpha_composite(layer)


def _glassy_card(img, x1, y1, x2, y2, radius=24):
    """Simula glassmorphism: fill escuro + borda brilhante."""
    # Fill semitransparente
    overlay_rect(img, x1, y1, x2, y2, (255, 255, 255, 8), radius=radius)
    # Borda
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=radius,
                        outline=(34, 197, 94, 60), width=1)
    img.alpha_composite(layer)


def criativo_revendedores():
    W, H = SIZE
    img  = Image.new("RGBA", SIZE)

    # ── Fundo: gradiente quasi-preto com toque roxo ───────────────────────
    gradient_v(img, (6, 4, 20), (14, 8, 42))

    # ── Decoracoes geometricas sutis ──────────────────────────────────────
    # Circulo grande verde no canto sup. direito (glow)
    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    gd.ellipse([(680, -320), (1380, 380)], fill=(34, 197, 94, 12))
    img.alpha_composite(glow)

    # Circulo roxo no canto inf. esq. (glow)
    glow2 = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    gd2   = ImageDraw.Draw(glow2)
    gd2.ellipse([(-280, 700), (420, 1400)], fill=(72, 44, 160, 30))
    img.alpha_composite(glow2)

    # Outlines de circulo decorativos
    _draw_circle_decoration(img, 960, 120, 200, (34, 197, 94, 18))
    _draw_circle_decoration(img, 960, 120, 280, (34, 197, 94, 10))
    _draw_circle_decoration(img, 120, 960, 160, (72, 44, 160, 25))

    # Linha horizontal sutil no meio
    layer_line = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer_line)
    ld.line([(0, H // 2), (W, H // 2)], fill=(255, 255, 255, 6), width=1)
    img.alpha_composite(layer_line)

    # ── Barra topo verde fina ─────────────────────────────────────────────
    overlay_rect(img, 0, 0, W, 3, (*GREEN_NEON, 255))

    draw = ImageDraw.Draw(img)

    # ── Logo pequeno + nome ───────────────────────────────────────────────
    paste_logo(img, 56, W // 2, 46)
    draw = ImageDraw.Draw(img)

    # ── Headline principal ────────────────────────────────────────────────
    h1f = fnt(52, "black")
    text_center(draw, "PROGRAMA DE PARCEIROS", h1f, 96, W, WHITE, shadow_fill=(0,0,0,80))

    sub_f = fnt(24, "regular")
    text_center(draw, "Construa sua renda revendendo um SaaS em pleno crescimento.",
                sub_f, 158, W, (*GRAY_SOFT,), shadow_fill=None)

    # ── Card central glassmorphism ────────────────────────────────────────
    card_y1, card_y2 = 208, 520
    _glassy_card(img, 54, card_y1, W - 54, card_y2, radius=28)
    draw = ImageDraw.Draw(img)

    # "COMISSAO RECORRENTE" label pequeno dentro do card
    lbl_f = fnt(19, "bold")
    bb    = draw.textbbox((0, 0), "COMISSAO RECORRENTE", font=lbl_f)
    lbl_w = bb[2] - bb[0]
    lbl_x = (W - lbl_w) // 2
    # pill fundo para o label
    overlay_rect(img, lbl_x - 16, 226, lbl_x + lbl_w + 16, 258,
                 (*GREEN_NEON, 20), radius=10)
    draw = ImageDraw.Draw(img)
    text_center(draw, "COMISSAO RECORRENTE", lbl_f, 230, W, (*GREEN_NEON,), shadow_fill=None)

    # "50%" hero number
    pct_f = fnt(200, "black")
    bb    = draw.textbbox((0, 0), "50%", font=pct_f)
    pw    = bb[2] - bb[0]
    ph    = bb[3] - bb[1]
    px    = (W - pw) // 2
    # Sombra verde suave
    draw.text((px + 4, 268 + 4), "50%", font=pct_f, fill=(*GREEN_NEON, 30))
    draw.text((px, 268), "50%", font=pct_f, fill=(*GREEN_NEON,))

    # "por cliente ativo, todo mes" abaixo
    rec_f = fnt(24, "bold")
    text_center(draw, "por cliente ativo, todo mes", rec_f, 478, W,
                (*GRAY_SOFT,), shadow_fill=None)

    # ── Linha divisora dentro do card ─────────────────────────────────────
    divider(img, 508, W, GREEN_NEON, alpha=25, margin=130)

    # ── Stats row (3 colunas) ─────────────────────────────────────────────
    stats = [
        ("500+",  "empresas\natendidas"),
        ("100%",  "online\nsem escritorio"),
        ("24h",   "suporte\nao revendedor"),
    ]
    stat_vf = fnt(36, "black")
    stat_lf = fnt(19, "regular")
    cols    = [270, 540, 810]
    sy      = 530

    for i, (val, lbl) in enumerate(stats):
        cx = cols[i]
        # Valor
        bb  = draw.textbbox((0, 0), val, font=stat_vf)
        vw  = bb[2] - bb[0]
        draw.text((cx - vw // 2 + 1, sy + 1), val, font=stat_vf, fill=(0,0,0,80))
        draw.text((cx - vw // 2, sy), val, font=stat_vf, fill=(*GREEN_NEON,))
        # Label (2 linhas)
        for j, line in enumerate(lbl.split("\n")):
            bb2 = draw.textbbox((0, 0), line, font=stat_lf)
            lw  = bb2[2] - bb2[0]
            draw.text((cx - lw // 2, sy + 44 + j * 24), line,
                      font=stat_lf, fill=(*GRAY_SOFT,))

        # Separador vertical entre colunas
        if i < 2:
            sep_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
            sd = ImageDraw.Draw(sep_layer)
            mid_x = (cols[i] + cols[i+1]) // 2
            sd.line([(mid_x, sy - 4), (mid_x, sy + 90)],
                    fill=(255, 255, 255, 25), width=1)
            img.alpha_composite(sep_layer)
            draw = ImageDraw.Draw(img)

    # ── Divisor principal ─────────────────────────────────────────────────
    divider(img, 644, W, WHITE, alpha=14, margin=54)

    # ── Beneficios em grid 2x2 ────────────────────────────────────────────
    benefits = [
        ("Renda passiva e recorrente",   "Suporte e treinamento incluso"),
        ("Painel exclusivo de vendas",   "Sem meta ou investimento inicial"),
    ]
    bf      = fnt(26, "bold")
    check_f = fnt(20, "bold")
    row_y   = 664
    col_l   = 90
    col_r   = 560

    for row in benefits:
        for ci, item in enumerate(row):
            cx = col_l if ci == 0 else col_r
            # checkmark verde
            overlay_rect(img, cx, row_y, cx + 32, row_y + 32,
                         (*GREEN_NEON, 220), radius=16)
            draw = ImageDraw.Draw(img)
            cb   = draw.textbbox((0, 0), "v", font=check_f)
            cw   = cb[2] - cb[0]
            draw.text((cx + 16 - cw // 2, row_y + 6), "v",
                      font=check_f, fill=BLACK)
            draw.text((cx + 44, row_y + 4), item, font=bf, fill=WHITE)
        row_y += 56

    # ── Urgencia ──────────────────────────────────────────────────────────
    urg_y  = row_y + 20
    urg_f  = fnt(22, "bold")
    urg_txt = "Apenas 5 vagas por regiao  —  Garanta a sua"
    bb      = draw.textbbox((0, 0), urg_txt, font=urg_f)
    uw      = bb[2] - bb[0]
    ux      = (W - uw - 40) // 2
    overlay_rect(img, ux, urg_y, ux + uw + 40, urg_y + 40,
                 (*GREEN_NEON, 15), radius=8)
    layer_urg = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    lu = ImageDraw.Draw(layer_urg)
    lu.rounded_rectangle([(ux, urg_y), (ux + uw + 40, urg_y + 40)],
                         radius=8, outline=(*GREEN_NEON, 100), width=1)
    img.alpha_composite(layer_urg)
    draw = ImageDraw.Draw(img)
    text_center(draw, urg_txt, urg_f, urg_y + 8, W,
                (*GRAY_SOFT,), shadow_fill=None)

    # ── CTA Button ────────────────────────────────────────────────────────
    cta_y = urg_y + 58
    cta_f = fnt(36, "black")
    pill_button(img, ImageDraw.Draw(img),
                "  Quero ser Parceiro  ", cta_f,
                cta_y, W, GREEN_NEON, BLACK, pad_x=60, pad_y=18)
    draw = ImageDraw.Draw(img)

    # ── URL rodape ────────────────────────────────────────────────────────
    url_f = fnt(20, "regular")
    text_center(draw, "topagenda.online", url_f, H - 38, W,
                (120, 120, 160, 180), shadow_fill=None)

    out = os.path.join(OUTPUT_DIR, "criativo_revendedores.png")
    img.convert("RGB").save(out, "PNG")
    print(f"[OK] Revendedores: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# STORY VERSIONS  1080 × 1920  (9:16)
# ═══════════════════════════════════════════════════════════════════════════

STORY = (1080, 1920)


def story_clientes():
    W, H = STORY
    img  = Image.new("RGBA", STORY)
    gradient_v(img, PURPLE_DEEP, (30, 15, 80))

    # Glow no topo direito
    glow = Image.new("RGBA", STORY, (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    gd.ellipse([(600, -300), (1500, 700)], fill=(*PURPLE_HERO, 50))
    img.alpha_composite(glow)

    # Glow verde no canto inferior
    glow2 = Image.new("RGBA", STORY, (0, 0, 0, 0))
    gd2   = ImageDraw.Draw(glow2)
    gd2.ellipse([(-200, 1400), (600, 2200)], fill=(*GREEN_NEON, 20))
    img.alpha_composite(glow2)

    # Decoracoes circulares
    _draw_circle_decoration(img, 980, 200, 280, (*GREEN_NEON, 15))
    _draw_circle_decoration(img, 980, 200, 380, (*GREEN_NEON, 8))

    # Barra topo
    overlay_rect(img, 0, 0, W, 4, (*GREEN_NEON, 255))

    draw = ImageDraw.Draw(img)

    # ── Logo ─────────────────────────────────────────────────────────────
    paste_logo(img, 90, W // 2, 80)
    draw = ImageDraw.Draw(img)

    # ── Badge tag ─────────────────────────────────────────────────────────
    tag_f = fnt(24, "bold")
    overlay_rect(img, 200, 148, 880, 186, (*GREEN_NEON, 20), radius=16)
    layer = Image.new("RGBA", STORY, (0, 0, 0, 0))
    ld    = ImageDraw.Draw(layer)
    ld.rounded_rectangle([(200, 148), (880, 186)], radius=16,
                         outline=(*GREEN_NEON, 180), width=2)
    img.alpha_composite(layer)
    draw = ImageDraw.Draw(img)
    text_center(draw, "SISTEMA DE AGENDAMENTO ONLINE", tag_f, 154, W,
                (*GREEN_NEON,), shadow_fill=None)

    # ── Headline ──────────────────────────────────────────────────────────
    h1f = fnt(88, "black")
    y   = 216
    for line in ["Sistema de", "Agendamento", "Online"]:
        bb  = draw.textbbox((0, 0), line, font=h1f)
        tw  = bb[2] - bb[0]
        th  = bb[3] - bb[1]
        draw.text(((W - tw) // 2 + 2, y + 2), line, font=h1f, fill=(0,0,0,100))
        draw.text(((W - tw) // 2, y), line, font=h1f, fill=WHITE)
        if line == "Online":
            overlay_rect(img, (W - tw) // 2, y + th + 4,
                         (W - tw) // 2 + tw, y + th + 10, (*GREEN_NEON, 255))
        y += th + 10

    y += 24

    # ── Subtítulo ─────────────────────────────────────────────────────────
    sub_f = fnt(30, "regular")
    for line in ["Seus clientes agendam 24h por dia,",
                 "sem precisar ligar ou mandar mensagem."]:
        h = text_height(draw, line, sub_f)
        text_center(draw, line, sub_f, y, W, (*GRAY_SOFT,), shadow_fill=None)
        y += h + 8
    y += 36

    # ── Mockup celular centralizado ────────────────────────────────────────
    phone_h = 680
    pw      = paste_phone(img, phone_h, (W - int(phone_h * 0.55)) // 2, y)
    y      += phone_h + 40

    # ── Divisor ───────────────────────────────────────────────────────────
    divider(img, y, W, GREEN_NEON, alpha=35, margin=80)
    y += 36

    # ── Features 2x2 ──────────────────────────────────────────────────────
    fi    = fnt(18, "bold")
    fb    = fnt(30, "bold")
    feats = [
        ("v", "Agendamento 24h automatico"),
        ("v", "Confirmacao pelo WhatsApp"),
        ("v", "Painel de controle completo"),
        ("v", "Teste gratis por 14 dias"),
    ]
    for icon, text in feats:
        y = bullet_row(img, ImageDraw.Draw(img), icon, text,
                       fi, fb, 100, y, GREEN_NEON)
        draw = ImageDraw.Draw(img)
    y += 40

    # ── CTA ───────────────────────────────────────────────────────────────
    cta_f = fnt(40, "black")
    pill_button(img, ImageDraw.Draw(img),
                "  Experimente GRATIS  ", cta_f,
                y, W, GREEN_NEON, BLACK, pad_x=60, pad_y=22)
    draw = ImageDraw.Draw(img)

    url_f = fnt(24, "regular")
    text_center(draw, "topagenda.online", url_f, H - 52, W,
                (*GRAY_SOFT, 180), shadow_fill=None)

    out = os.path.join(OUTPUT_DIR, "story_clientes.png")
    img.convert("RGB").save(out, "PNG")
    print(f"[OK] Story clientes: {out}")
    return out


def story_revendedores():
    W, H = STORY   # 1080 × 1920
    img  = Image.new("RGBA", STORY)
    gradient_v(img, (6, 4, 20), (14, 8, 42))

    # Glows
    glow = Image.new("RGBA", STORY, (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    gd.ellipse([(550, -450), (1650, 750)],  fill=(*GREEN_NEON, 10))
    gd.ellipse([(-350, 1400), (500, 2200)], fill=(*PURPLE_HERO, 22))
    img.alpha_composite(glow)

    _draw_circle_decoration(img, 980, 300,  280, (*GREEN_NEON, 14))
    _draw_circle_decoration(img, 980, 300,  390, (*GREEN_NEON, 7))
    _draw_circle_decoration(img, 100, 1680, 200, (*PURPLE_HERO, 28))
    _draw_circle_decoration(img, 100, 1680, 280, (*PURPLE_HERO, 14))

    overlay_rect(img, 0, 0, W, 4, (*GREEN_NEON, 255))

    draw = ImageDraw.Draw(img)

    # ── Ancoras proporcionais ao height ───────────────────────────────────
    LOGO_CY = int(H * 0.065)
    H1_Y    = int(H * 0.105)
    CARD_Y1 = int(H * 0.230)
    CARD_Y2 = int(H * 0.510)
    STATS_Y = int(H * 0.535)
    DIV_Y   = int(H * 0.628)
    BENE_Y  = int(H * 0.648)
    URG_Y   = int(H * 0.825)
    CTA_Y   = int(H * 0.862)
    SWIPE_Y = int(H * 0.940)
    URL_Y   = int(H * 0.972)

    # ── Logo ─────────────────────────────────────────────────────────────
    paste_logo(img, 96, W // 2, LOGO_CY)
    draw = ImageDraw.Draw(img)

    # ── Headline (2 linhas) ───────────────────────────────────────────────
    h1f = fnt(80, "black")
    y_h = H1_Y
    for line in ["PROGRAMA", "DE PARCEIROS"]:
        bb  = draw.textbbox((0, 0), line, font=h1f)
        tw  = bb[2] - bb[0]
        th  = bb[3] - bb[1]
        draw.text(((W - tw) // 2 + 2, y_h + 2), line, font=h1f, fill=(0,0,0,90))
        draw.text(((W - tw) // 2, y_h), line, font=h1f, fill=WHITE)
        y_h += th + 6

    sub_f = fnt(30, "regular")
    text_center(draw, "Revenda um SaaS em pleno crescimento.",
                sub_f, y_h + 10, W, (*GRAY_SOFT,), shadow_fill=None)

    # ── Card glassmorphism (50%) ──────────────────────────────────────────
    card_y1, card_y2 = CARD_Y1, CARD_Y2
    _glassy_card(img, 54, card_y1, W - 54, card_y2, radius=32)
    draw = ImageDraw.Draw(img)

    lbl_f  = fnt(24, "bold")
    lbl_y1 = card_y1 + 22
    lbl_y2 = lbl_y1 + 38
    overlay_rect(img, 340, lbl_y1, 740, lbl_y2, (*GREEN_NEON, 20), radius=12)
    draw = ImageDraw.Draw(img)
    text_center(draw, "COMISSAO RECORRENTE", lbl_f, lbl_y1 + 7, W,
                (*GREEN_NEON,), shadow_fill=None)

    # "50%" hero
    pct_f  = fnt(270, "black")
    pct_y  = lbl_y2 + 20
    bb     = draw.textbbox((0, 0), "50%", font=pct_f)
    pw_    = bb[2] - bb[0]
    px_    = (W - pw_) // 2
    draw.text((px_ + 5, pct_y + 5), "50%", font=pct_f, fill=(*GREEN_NEON, 22))
    draw.text((px_, pct_y), "50%", font=pct_f, fill=(*GREEN_NEON,))

    rec_f = fnt(30, "bold")
    rec_y = card_y2 - 46
    text_center(draw, "por cliente ativo, todo mes", rec_f, rec_y, W,
                (*GRAY_SOFT,), shadow_fill=None)

    # Divisor interno ao card
    divider(img, card_y2 - 8, W, GREEN_NEON, alpha=18, margin=120)

    # ── Stats row ─────────────────────────────────────────────────────────
    stats   = [("500+", "empresas\natendidas"),
               ("100%", "online\nsem escritorio"),
               ("24h",  "suporte\nao parceiro")]
    stat_vf = fnt(50, "black")
    stat_lf = fnt(24, "regular")
    cols    = [270, 540, 810]
    sy      = STATS_Y

    for i, (val, lbl) in enumerate(stats):
        cx  = cols[i]
        bb  = draw.textbbox((0, 0), val, font=stat_vf)
        vw  = bb[2] - bb[0]
        draw.text((cx - vw // 2 + 2, sy + 2), val, font=stat_vf, fill=(0,0,0,80))
        draw.text((cx - vw // 2, sy), val, font=stat_vf, fill=(*GREEN_NEON,))
        for j, line in enumerate(lbl.split("\n")):
            bb2 = draw.textbbox((0, 0), line, font=stat_lf)
            lw  = bb2[2] - bb2[0]
            draw.text((cx - lw // 2, sy + 60 + j * 30), line,
                      font=stat_lf, fill=(*GRAY_SOFT,))
        if i < 2:
            sep_l = Image.new("RGBA", STORY, (0, 0, 0, 0))
            sd    = ImageDraw.Draw(sep_l)
            mid_x = (cols[i] + cols[i+1]) // 2
            sd.line([(mid_x, sy - 4), (mid_x, sy + 120)],
                    fill=(255, 255, 255, 22), width=1)
            img.alpha_composite(sep_l)
            draw = ImageDraw.Draw(img)

    # ── Divisor principal ─────────────────────────────────────────────────
    divider(img, DIV_Y, W, WHITE, alpha=12, margin=54)

    # ── Beneficios (1 coluna, sem corte) ──────────────────────────────────
    bf      = fnt(33, "bold")
    check_f = fnt(22, "bold")
    benefits_list = [
        "Renda passiva e recorrente",
        "Painel exclusivo de vendas",
        "Suporte e treinamento incluso",
        "Sem meta ou investimento inicial",
    ]
    row_y = BENE_Y
    for item in benefits_list:
        bx = 90
        overlay_rect(img, bx, row_y, bx + 36, row_y + 36,
                     (*GREEN_NEON, 220), radius=18)
        draw = ImageDraw.Draw(img)
        cb   = draw.textbbox((0, 0), "v", font=check_f)
        cw   = cb[2] - cb[0]
        draw.text((bx + 18 - cw // 2, row_y + 8), "v", font=check_f, fill=BLACK)
        draw.text((bx + 52, row_y + 4), item, font=bf, fill=WHITE)
        row_y += 72

    # ── Urgencia ──────────────────────────────────────────────────────────
    urg_y   = URG_Y
    urg_f   = fnt(27, "bold")
    urg_txt = "Apenas 5 vagas por regiao  —  Garanta a sua"
    bb      = draw.textbbox((0, 0), urg_txt, font=urg_f)
    uw      = bb[2] - bb[0]
    ux      = (W - uw - 52) // 2
    overlay_rect(img, ux, urg_y, ux + uw + 52, urg_y + 52,
                 (*GREEN_NEON, 14), radius=10)
    layer_urg = Image.new("RGBA", STORY, (0, 0, 0, 0))
    lu = ImageDraw.Draw(layer_urg)
    lu.rounded_rectangle([(ux, urg_y), (ux + uw + 52, urg_y + 52)],
                         radius=10, outline=(*GREEN_NEON, 100), width=1)
    img.alpha_composite(layer_urg)
    draw = ImageDraw.Draw(img)
    text_center(draw, urg_txt, urg_f, urg_y + 12, W, (*GRAY_SOFT,), shadow_fill=None)

    # ── CTA ───────────────────────────────────────────────────────────────
    cta_y = CTA_Y
    cta_f = fnt(44, "black")
    pill_button(img, ImageDraw.Draw(img),
                "  Quero ser Parceiro  ", cta_f,
                cta_y, W, GREEN_NEON, BLACK, pad_x=70, pad_y=24)
    draw = ImageDraw.Draw(img)

    sw_f = fnt(24, "regular")
    text_center(draw, "Deslize para saber mais",
                sw_f, SWIPE_Y, W, (100, 100, 140, 200), shadow_fill=None)

    url_f = fnt(23, "regular")
    text_center(draw, "topagenda.online", url_f, URL_Y, W,
                (100, 100, 140, 180), shadow_fill=None)

    out = os.path.join(OUTPUT_DIR, "story_revendedores.png")
    img.convert("RGB").save(out, "PNG")
    print(f"[OK] Story revendedores: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Gerando criativos Top Agenda...\n")
    criativo_clientes()
    criativo_revendedores()
    story_clientes()
    story_revendedores()
    print("\nPronto! 4 arquivos gerados em output/")
