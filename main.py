"""
Ponto de entrada principal.
Uso:
  python main.py            → inicia o agendador (modo VPS/produção)
  python main.py --now      → executa o pipeline imediatamente (teste)
  python main.py --test     → testa apenas geração (sem publicar)
"""
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Top Agenda Instagram Bot")
    parser.add_argument("--now", action="store_true", help="Executa pipeline agora")
    parser.add_argument("--test", action="store_true", help="Testa geração sem publicar")
    args = parser.parse_args()

    # Inicia listener de comandos Telegram em background (sempre)
    import telegram_bot
    telegram_bot.start_background()

    if args.test:
        print("[Main] Modo de teste: gerando conteúdo sem publicar...\n")
        import os
        os.environ["INSTAGRAM_ACCESS_TOKEN"] = ""  # força modo simulação
        import pipeline
        result = pipeline.run()
        print(f"\n[Main] Resultado: {result.get('status')}")
        if result.get("status") == "published":
            print(f"  Score: {result.get('score')}")
            print(f"  Imagens: {result.get('images_count')}")

    elif args.now:
        print("[Main] Executando pipeline agora...\n")
        import pipeline
        result = pipeline.run()
        print(f"\n[Main] Resultado: {result.get('status')}")

    else:
        import scheduler
        scheduler.start()


if __name__ == "__main__":
    main()
