"""
Agente 6 - Publisher
Publica o conteúdo no Instagram via Graph API.
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from config import (
    INSTAGRAM_USER_ID, INSTAGRAM_ACCESS_TOKEN,
    PUBLIC_IMAGE_BASE_URL, OUTPUT_DIR
)

GRAPH_API = "https://graph.facebook.com/v21.0"


def _upload_to_public_host(filepath: str) -> str:
    """Faz upload da imagem para catbox.moe e retorna URL pública."""
    print(f"  [Publisher] Fazendo upload de {os.path.basename(filepath)}...")
    with open(filepath, "rb") as f:
        response = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (os.path.basename(filepath), f, "image/jpeg")},
            timeout=60
        )
    url = response.text.strip()
    if not url.startswith("https://"):
        raise Exception(f"Upload falhou: {url}")
    print(f"  [Publisher] URL pública: {url}")
    return url


def _get_public_url(filepath: str) -> str:
    """Obtém URL pública — faz upload para host externo para garantir acesso do Instagram."""
    return _upload_to_public_host(filepath)


def _create_media_container(image_url: str, caption: str = None, is_carousel_item: bool = False) -> str:
    """Cria container de mídia no Instagram. Retorna container ID. Retry em erros transientes."""
    params = {
        "image_url": image_url,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    if is_carousel_item:
        params["is_carousel_item"] = "true"
    elif caption:
        params["caption"] = caption

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        response = requests.post(
            f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media",
            params=params,
            timeout=30
        )
        data = response.json()

        if "id" in data:
            return data["id"]

        error = data.get("error", {})
        is_transient = error.get("is_transient", False)

        if is_transient and attempt < max_retries:
            wait = 10 * attempt
            print(f"  [Publisher] Erro transiente (tentativa {attempt}/{max_retries}), aguardando {wait}s...")
            time.sleep(wait)
            continue

        raise Exception(f"Erro ao criar container: {data}")

    raise Exception("Falha ao criar container após todas as tentativas")


def _wait_for_container(container_id: str, max_wait: int = 60) -> bool:
    """Aguarda o container estar pronto para publicação."""
    for _ in range(max_wait // 5):
        response = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={
                "fields": "status_code",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            },
            timeout=15
        )
        status = response.json().get("status_code")

        if status == "FINISHED":
            return True
        elif status == "ERROR":
            return False

        time.sleep(5)

    return False


def _publish_container(container_id: str) -> dict:
    """Publica o container. Retorna o ID do post publicado."""
    response = requests.post(
        f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        },
        timeout=30
    )
    return response.json()


def _publish_single(image_path: str, caption: str) -> dict:
    """Publica um post simples (1 imagem)."""
    url = _get_public_url(image_path)
    print(f"  [Publisher] Criando container para: {url}")

    container_id = _create_media_container(url, caption=caption)
    print(f"  [Publisher] Container criado: {container_id}")

    if not _wait_for_container(container_id):
        raise Exception("Container não ficou pronto no tempo esperado")

    result = _publish_container(container_id)
    return result


def _upload_and_create(args) -> tuple:
    """Upload + criação de container em paralelo. Retorna (index, item_id)."""
    i, path = args
    url = _get_public_url(path)
    print(f"  [Publisher] Criando item {i + 1}: {url}")
    item_id = _create_media_container(url, is_carousel_item=True)
    return i, item_id


def _publish_carousel(image_paths: list, caption: str) -> dict:
    """Publica um carrossel — uploads em paralelo para reduzir tempo."""
    item_ids_map = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_upload_and_create, (i, path)): i
                   for i, path in enumerate(image_paths)}
        for future in as_completed(futures):
            i, item_id = future.result()
            item_ids_map[i] = item_id

    # Garante ordem correta dos slides
    item_ids = [item_ids_map[i] for i in sorted(item_ids_map)]
    print(f"  [Publisher] {len(item_ids)} itens carregados em paralelo")

    # Cria container do carrossel (com retry para erros transientes)
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(item_ids),
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    data = None
    for attempt in range(1, 4):
        response = requests.post(
            f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media",
            params=params,
            timeout=30
        )
        data = response.json()

        if "id" in data:
            break

        error = data.get("error", {})
        if error.get("is_transient") and attempt < 3:
            wait = 10 * attempt
            print(f"  [Publisher] Erro transiente no carrossel (tentativa {attempt}/3), aguardando {wait}s...")
            time.sleep(wait)
            continue

        raise Exception(f"Erro ao criar carrossel: {data}")

    if "id" not in data:
        raise Exception(f"Erro ao criar carrossel após retries: {data}")

    carousel_id = data["id"]
    print(f"  [Publisher] Container do carrossel: {carousel_id}")

    if not _wait_for_container(carousel_id):
        raise Exception("Carrossel não ficou pronto no tempo esperado")

    return _publish_container(carousel_id)


def _publish_story(story_path: str) -> dict:
    """Publica imagem como Story."""
    try:
        url = _get_public_url(story_path)
        print(f"  [Publisher] Criando Story: {url}")

        response = requests.post(
            f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media",
            params={
                "image_url": url,
                "media_type": "STORIES",
                "access_token": INSTAGRAM_ACCESS_TOKEN,
            },
            timeout=30
        )
        data = response.json()
        if "id" not in data:
            raise Exception(f"Erro ao criar story container: {data}")

        story_id = data["id"]
        if not _wait_for_container(story_id):
            raise Exception("Story container não ficou pronto")

        result = _publish_container(story_id)
        if "id" in result:
            print(f"  [Publisher] Story publicado! ID: {result['id']}")
        return result
    except Exception as e:
        print(f"  [Publisher] ERRO no story: {e}")
        return {"error": str(e)}


def run(edited: dict, script: dict, strategy: dict) -> dict:
    """
    Publica feed + story no Instagram.
    `edited` é o dict retornado pelo editor: {"feed": [...], "story": path}
    """
    # Suporte ao formato antigo (lista) e novo (dict)
    if isinstance(edited, list):
        image_paths = edited
        story_path  = None
    else:
        image_paths = edited.get("feed", [])
        story_path  = edited.get("story")

    if not INSTAGRAM_USER_ID or not INSTAGRAM_ACCESS_TOKEN:
        print("  [Publisher] SIMULAÇÃO (token não configurado)")
        return {"simulated": True, "caption_preview": script.get("caption", "")[:100]}

    hashtags_str = " ".join(script.get("hashtags", []))
    caption = f"{script.get('caption', '')}\n\n{hashtags_str}"
    content_type = strategy.get("content_type", "single_post")

    try:
        # ── Publica feed ──────────────────────────────────────
        if len(image_paths) > 1 or content_type == "carousel":
            result = _publish_carousel(image_paths, caption)
        else:
            result = _publish_single(image_paths[0], caption)

        if "id" in result:
            print(f"  [Publisher] Feed publicado! Post ID: {result['id']}")
        else:
            return {"error": str(result)}

        # ── Publica story ─────────────────────────────────────
        story_result = None
        if story_path and os.path.exists(story_path):
            time.sleep(3)
            story_result = _publish_story(story_path)

        result["story"] = story_result
        return result

    except Exception as e:
        print(f"  [Publisher] ERRO: {e}")
        return {"error": str(e)}
