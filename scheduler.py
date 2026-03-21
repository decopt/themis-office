"""
Agendador de publicações automáticas.
"""
import signal
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import POST_TIMES, MAX_POSTS_PER_DAY
import pipeline

scheduler = BlockingScheduler(timezone="America/Sao_Paulo")


def scheduled_job():
    """Job executado nos horários agendados."""
    from pipeline import _count_posts_today
    count = _count_posts_today()

    if count >= MAX_POSTS_PER_DAY:
        print(f"[Scheduler] Limite diário atingido ({count}/{MAX_POSTS_PER_DAY}). Pulando.")
        return

    print(f"[Scheduler] Executando pipeline ({count + 1}/{MAX_POSTS_PER_DAY} hoje)...")
    pipeline.run()


def start():
    """Inicia o agendador."""
    print("=" * 50)
    print("Top Agenda - Instagram Bot")
    print("=" * 50)
    print(f"Horários configurados: {POST_TIMES}")
    print(f"Máximo por dia: {MAX_POSTS_PER_DAY}")
    print(f"Timezone: America/Sao_Paulo")
    print("=" * 50)

    for time_str in POST_TIMES:
        hour, minute = time_str.strip().split(":")
        scheduler.add_job(
            scheduled_job,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id=f"post_{hour}_{minute}",
            name=f"Post às {time_str}"
        )
        print(f"Agendado: {time_str}")

    def shutdown(signum, frame):
        print("\n[Scheduler] Encerrando...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print("\nAguardando horários agendados... (Ctrl+C para parar)\n")
    scheduler.start()


if __name__ == "__main__":
    start()
