"""
Agente 3 - Designer
Gera imagens com Nano Banana Pro (modelo de imagem do Google).
"""
import os
import uuid
import random
from google import genai
from google.genai import types
from config import GOOGLE_API_KEY, GEMINI_CREATIVE_MODEL, OUTPUT_DIR

client = genai.Client(api_key=GOOGLE_API_KEY)

# Nichos de pequenos negocios brasileiros que usam o Top Agenda
BUSINESS_NICHES = [
    "Brazilian hairdresser styling a client's hair in a modern beauty salon, warm ambient lighting, professional atmosphere",
    "Brazilian barber giving a precise fade haircut in a contemporary barbershop, confident client in the chair",
    "Brazilian manicurist carefully applying nail polish at a clean, well-lit professional table",
    "Brazilian nutritionist in a bright modern clinic, consulting with a smiling patient, healthy foods visible",
    "Pedicure professional working in a cozy Brazilian beauty salon, clean setting, relaxed client",
    "Brazilian aesthetician performing a facial treatment in a clean white modern clinic, calm serene mood",
    "Personal trainer coaching a client in a small Brazilian gym, energetic and focused atmosphere",
    "Brazilian massage therapist in a calm wellness studio, warm soft lighting, professional setting",
    "Brazilian physiotherapist treating a patient in a modern rehabilitation clinic",
    "Brazilian tattoo artist focused on detailed work, clean studio with colorful artwork on the walls",
    "Brazilian eyebrow designer working precisely on a client in a well-lit beauty studio",
    "Brazilian dentist in a modern clean dental clinic, professional and welcoming atmosphere",
]


def _build_image_prompt(slide: dict, strategy: dict, niche: str) -> str:
    tone = strategy.get("tone", "professional and warm")

    # Prioriza a descricao especifica do slide (gerada pelo scriptwriter)
    slide_desc = slide.get("image_description", "")
    if slide_desc and len(slide_desc) > 20:
        scene = slide_desc
    else:
        scene = niche

    return f"""High-quality editorial photograph for Brazilian Instagram: {scene}.
The professional briefly glances at a smartphone showing a clean digital scheduling app — organized calendar view, minimal modern UI with blue interface tones.
Mood: {tone}, aspirational, authentic. Real Brazilian small business environment.
Style: natural warm lighting, shallow depth of field, photorealistic DSLR quality, sharp focus on the professional.
Composition: rule of thirds, professional in foreground, workplace context visible in background.
Color palette: the scene should naturally incorporate the brand identity colors — dominant medium blue (#1B6FBB) in ambient lighting, clothing accents or props; complementary green (#4DB648) in small details like plants or decor; warm yellow (#FFC107) as a highlight accent. Background tones: deep navy-to-midnight-blue gradient feel. Overall: professional, clean, modern, trustworthy.
NO text, NO letters, NO numbers, NO watermarks, NO logos anywhere in the image.
Square 1:1 format, high resolution."""


def run(script: dict, strategy: dict) -> list:
    """
    Gera imagens para todos os slides com Nano Banana Pro.
    Retorna lista de caminhos de arquivo.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image_paths = []
    post_id = str(uuid.uuid4())[:8]

    # Escolhe nichos aleatórios (sem repetir no mesmo post)
    niches = random.sample(BUSINESS_NICHES, min(len(script.get("slides", [])), len(BUSINESS_NICHES)))

    for i, slide in enumerate(script.get("slides", [])):
        slide_num = slide.get("slide_number", 1)
        niche = niches[i % len(niches)]
        prompt = _build_image_prompt(slide, strategy, niche)

        print(f"  [Designer] Gerando imagem {slide_num} com Nano Banana Pro...")

        response = client.models.generate_content(
            model=GEMINI_CREATIVE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                filename = f"{post_id}_slide{slide_num}.png"
                filepath = os.path.join(OUTPUT_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(part.inline_data.data)
                image_paths.append(filepath)
                print(f"  [Designer] Imagem salva: {filename} ({len(part.inline_data.data)//1024}KB)")
                image_saved = True
                break

        if not image_saved:
            print(f"  [Designer] AVISO: Nano Banana não retornou imagem para slide {slide_num}, tentando Imagen 4...")
            # Fallback para Imagen 4
            from google.genai import types as t
            fb = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=t.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1")
            )
            if fb.generated_images:
                filename = f"{post_id}_slide{slide_num}.png"
                filepath = os.path.join(OUTPUT_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(fb.generated_images[0].image.image_bytes)
                image_paths.append(filepath)
                print(f"  [Designer] Fallback Imagen 4 OK: {filename}")

    return image_paths
