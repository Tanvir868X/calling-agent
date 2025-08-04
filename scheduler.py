from apscheduler.schedulers.blocking import BlockingScheduler
from rag_ingest import process_files

scheduler = BlockingScheduler()

def daily_ingest():
    print("🔄 Starting FAQ sync...")
    process_files()

# 🕒 Run once immediately
daily_ingest()

# ⏳ Also schedule it daily at 1AM if needed
scheduler.add_job(daily_ingest, "cron", hour=1)

if __name__ == "__main__":
    print("⏳ Scheduler running... (daily sync at 1AM)")
    scheduler.start()
