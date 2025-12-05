import time
from jobs.housekeeper_job import HousekeeperJob


INTERVAL_SECONDS = 600   # run every 10 minutes
AGE_THRESHOLD = 60       # delete jobs older than 1 minute


def main():
    print("🧹 OpenLP Scheduler started")
    print(f"⏱ Running every {INTERVAL_SECONDS} seconds")
    print(f"🔥 Cleaning jobs older than {AGE_THRESHOLD} seconds\n")

    while True:
        try:
            HousekeeperJob(max_age=AGE_THRESHOLD).run()
        except Exception as e:
            print("❌ Housekeeper failed:", e)

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
