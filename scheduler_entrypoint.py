import time
from jobs.housekeeper_job import HousekeeperJob

INTERVAL_SECONDS = 600   # 10 minutes
AGE_THRESHOLD = 60       # delete jobs older than 1 minute

def run_scheduler():
    print("🧹 OpenLP Scheduler started")
    print(f"⏱ Running every {INTERVAL_SECONDS} seconds")
    print(f"🔥 Cleaning jobs older than {AGE_THRESHOLD} seconds")

    while True:
        try:
            HousekeeperJob(max_age=AGE_THRESHOLD).run()
        except Exception as e:
            print(f"❌ Scheduler error: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    run_scheduler()
