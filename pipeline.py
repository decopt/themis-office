"""
Pipeline principal: orquestra todos os agentes em sequência.
"""
import json
import os
import traceback
import uuid
from datetime import datetime
from agents import strategist, scriptwriter, designer, html_editor, editor, reviewer, telegram_approver, publisher
from agents import researcher
from config import OUTPUT_DIR
import state

MAX_RETRIES = 2
LOG_FILE = os.path.join(OUTPUT_DIR, "pipeline_log.json")


def _log(entry: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    entry["timestamp"] = datetime.now().isoformat()
    logs.append(entry)
    logs = logs[-100:]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def _count_posts_today() -> int:
    if not os.path.exists(LOG_FILE):
        return 0
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except Exception:
        return 0
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(
        1 for log in logs
        if log.get("timestamp", "").startswith(today)
        and log.get("status") == "published"
    )


def run() -> dict:
    start_time = datetime.now()
    run_id = str(uuid.uuid4())[:8]
    post_count = _count_posts_today()

    print(f"\n{'='*50}")
    print(f"[Pipeline] Iniciando: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"[Pipeline] Posts publicados hoje: {post_count}")
    print(f"{'='*50}\n")

    state.set_running(run_id)

    # ── Agente 0: Pesquisador ───────────────────────────────
    state.set_agent("researcher", "running")
    print(f"[Agente 0] Pesquisador — carregando referencias...")
    research_context = researcher.run()
    state.set_agent("researcher", "done", f"{len(research_context)} chars de contexto")

    strategy = None
    script = None
    image_paths = []
    edited_paths = []
    review_result = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            # ── Agente 1: Estrategista ──────────────────────────
            state.set_agent("strategist", "running")
            print(f"[Agente 1] Estrategista (tentativa {attempt})...")
            if attempt == 1 or strategy is None:
                strategy = strategist.run(post_count_today=post_count, research_context=research_context)
                print(f"  Tema: {strategy.get('theme')}")
            state.set_agent("strategist", "done", strategy.get("theme"))

            # ── Agente 2: Roteirista ────────────────────────────
            state.set_agent("scriptwriter", "running")
            print(f"\n[Agente 2] Roteirista...")
            script = scriptwriter.run(strategy)
            print(f"  Slides: {len(script.get('slides', []))}")
            state.set_agent("scriptwriter", "done", f"{len(script.get('slides',[]))} slides")

            # ── Agente 3: Designer ──────────────────────────────
            state.set_agent("designer", "running")
            print(f"\n[Agente 3] Designer (gradient backgrounds)...")
            image_paths = designer.run(script, strategy)
            print(f"  Imagens geradas: {len(image_paths)}")
            if not image_paths:
                raise Exception("Designer não gerou nenhuma imagem")
            state.set_agent("designer", "done", f"{len(image_paths)} imagens")

            # ── Agente 4: Editor HTML+Playwright ───────────────
            state.set_agent("editor", "running")
            print(f"\n[Agente 4] HTML Editor (Playwright)...")
            edited = html_editor.run(image_paths, script, strategy)
            edited_paths = edited["feed"] if isinstance(edited, dict) else edited
            story_path = edited.get("story") if isinstance(edited, dict) else None
            print(f"  Imagens editadas: {len(edited_paths)}")
            if story_path:
                print(f"  Story gerado: {os.path.basename(story_path)}")
            state.set_agent("editor", "done", f"{len(edited_paths)} slides + story")

            # Limpa PNGs brutos — economiza disco (JPGs editados ja foram gerados)
            for raw in image_paths:
                try:
                    if os.path.exists(raw):
                        os.remove(raw)
                except Exception:
                    pass

            # ── Agente 5: Revisor ───────────────────────────────
            state.set_agent("reviewer", "running")
            print(f"\n[Agente 5] Revisor...")
            review_result = reviewer.run(strategy, script, edited_paths)
            score = review_result.get("score", 0)

            MIN_SCORE = 80

            if score < MIN_SCORE or not review_result.get("approved"):
                issues = review_result.get("issues", [])
                suggestions = review_result.get("suggestions", "")
                state.set_agent("reviewer", "error", f"Score {score} - abaixo de {MIN_SCORE}")
                print(f"  Reprovado. Score: {score}/100. Issues: {issues}")
                if attempt <= MAX_RETRIES:
                    print(f"  Refazendo (tentativa {attempt+1})...")
                    strategy["revision_notes"] = suggestions
                    strategy["previous_issues"] = issues
                    continue
                else:
                    # Score ainda abaixo do mínimo após todas as tentativas — não publica
                    print(f"  Score {score} abaixo de {MIN_SCORE} após {attempt} tentativas. Cancelando.")
                    log_entry = {
                        "status": "cancelled",
                        "run_id": run_id,
                        "content_type": strategy.get("content_type"),
                        "theme": strategy.get("theme"),
                        "score": score,
                        "images": [os.path.basename(p) for p in edited_paths],
                        "images_count": len(edited_paths),
                        "caption_preview": (script.get("caption", "")[:120] + "...") if script else "",
                        "hashtags_count": len(script.get("hashtags", [])) if script else 0,
                        "duration_seconds": (datetime.now() - start_time).seconds,
                        "result": {"cancelled": f"Score {score} abaixo do mínimo {MIN_SCORE}"},
                        "attempt": attempt,
                    }
                    _log(log_entry)
                    state.set_done(False, log_entry)
                    return log_entry
            else:
                state.set_agent("reviewer", "done", f"Score {score}/100 OK")

            # ── Agente 6: Aprovador Telegram ────────────────────
            state.set_agent("telegram_approver", "running")
            print(f"\n[Agente 6] Aprovador Telegram...")
            decision = telegram_approver.run(edited_paths, script, strategy, review_result)
            action = decision.get("action")
            print(f"  Decisao: {action}")

            if action == "reject":
                state.set_agent("telegram_approver", "error", "Rejeitado pelo admin")
                log_entry = {
                    "status": "rejected",
                    "run_id": run_id,
                    "content_type": strategy.get("content_type"),
                    "theme": strategy.get("theme"),
                    "score": score,
                    "images": [os.path.basename(p) for p in edited_paths],
                    "duration_seconds": (datetime.now() - start_time).seconds,
                    "result": {"rejected": "Admin rejeitou via Telegram"},
                    "attempt": attempt,
                }
                _log(log_entry)
                state.set_done(False, log_entry)
                return log_entry

            elif action == "timeout":
                state.set_agent("telegram_approver", "error", "Timeout sem resposta")
                log_entry = {
                    "status": "timeout",
                    "run_id": run_id,
                    "content_type": strategy.get("content_type"),
                    "theme": strategy.get("theme"),
                    "score": score,
                    "images": [os.path.basename(p) for p in edited_paths],
                    "duration_seconds": (datetime.now() - start_time).seconds,
                    "result": {"timeout": "Sem resposta do admin em 10 minutos"},
                    "attempt": attempt,
                }
                _log(log_entry)
                state.set_done(False, log_entry)
                return log_entry

            elif action == "schedule":
                scheduled_time = decision.get("scheduled_time", "indefinido")
                state.set_agent("telegram_approver", "done", f"Agendado para {scheduled_time}")
                log_entry = {
                    "status": "scheduled",
                    "run_id": run_id,
                    "content_type": strategy.get("content_type"),
                    "theme": strategy.get("theme"),
                    "score": score,
                    "images": [os.path.basename(p) for p in edited_paths],
                    "scheduled_time": scheduled_time,
                    "duration_seconds": (datetime.now() - start_time).seconds,
                    "result": {"scheduled": scheduled_time},
                    "attempt": attempt,
                }
                _log(log_entry)
                state.set_done(True, log_entry)
                return log_entry

            elif action == "recreate":
                state.set_agent("telegram_approver", "error", "Recriar solicitado pelo admin")
                print("  Admin solicitou recriar — regenerando conteudo...")
                strategy["revision_notes"] = "Admin solicitou recriar o post via Telegram."
                script = None
                image_paths = []
                edited_paths = []
                review_result = None
                if attempt <= MAX_RETRIES:
                    continue
                else:
                    log_entry = {
                        "status": "cancelled",
                        "run_id": run_id,
                        "content_type": strategy.get("content_type"),
                        "theme": strategy.get("theme"),
                        "duration_seconds": (datetime.now() - start_time).seconds,
                        "result": {"cancelled": "Recriar solicitado mas tentativas esgotadas"},
                        "attempt": attempt,
                    }
                    _log(log_entry)
                    state.set_done(False, log_entry)
                    return log_entry

            # action == "approve" — segue para publicacao
            state.set_agent("telegram_approver", "done", "Aprovado pelo admin")

            # ── Agente 7: Publisher (com retry proprio) ────────
            result = None
            pub_retries = 3
            for pub_attempt in range(1, pub_retries + 1):
                state.set_agent("publisher", "running")
                print(f"\n[Agente 6] Publisher (tentativa {pub_attempt}/{pub_retries})...")
                result = publisher.run(edited, script, strategy)

                success = not result.get("error") and not result.get("simulated")

                if success:
                    state.set_agent("publisher", "done", f"Post ID: {result.get('id','simulado')}")
                    break
                elif result.get("simulated"):
                    state.set_agent("publisher", "done", "Simulado (sem token)")
                    break
                else:
                    error_msg = str(result.get("error", ""))[:80]
                    state.set_agent("publisher", "error", error_msg)
                    if pub_attempt < pub_retries:
                        import time as _time
                        wait = 15 * pub_attempt
                        print(f"  [Publisher] Falhou, tentando novamente em {wait}s...")
                        _time.sleep(wait)
                    else:
                        print(f"  [Publisher] Falhou após {pub_retries} tentativas")

            duration = (datetime.now() - start_time).seconds
            success = not result.get("error") and not result.get("simulated")

            log_entry = {
                "status": "published" if success else ("simulated" if result.get("simulated") else "error"),
                "run_id": run_id,
                "content_type": strategy.get("content_type"),
                "theme": strategy.get("theme"),
                "main_message": strategy.get("main_message"),
                "score": score,
                "images": [os.path.basename(p) for p in edited_paths],
                "images_count": len(edited_paths),
                "caption_preview": (script.get("caption", "")[:120] + "...") if script else "",
                "hashtags_count": len(script.get("hashtags", [])) if script else 0,
                "duration_seconds": duration,
                "result": result,
                "attempt": attempt,
            }
            _log(log_entry)
            state.set_done(True, log_entry)

            print(f"\n{'='*50}")
            print(f"[Pipeline] Concluído em {duration}s")
            print(f"{'='*50}\n")

            return log_entry

        except Exception as e:
            print(f"\n[Pipeline] ERRO na tentativa {attempt}: {e}")
            traceback.print_exc()
            agent_id = state.get().get("current_agent")
            if agent_id:
                state.set_agent(agent_id, "error", str(e)[:80])

            if attempt > MAX_RETRIES:
                log_entry = {"status": "failed", "run_id": run_id, "error": str(e), "attempt": attempt}
                _log(log_entry)
                state.set_done(False, log_entry)
                return log_entry

    return {"status": "failed", "error": "Todas as tentativas falharam"}
