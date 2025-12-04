import os
import shutil
import time
from jobs import redis_conn
from services.openlp_service import TMP_DIR


class HousekeeperJob:
    """
    Periodic job that:
    - deletes jobs scheduled for cleanup (cleanup_at <= now)
    - removes orphaned directories older than 24 hours
    """

    def run(self):
        now = int(time.time())

        print("🧹 Housekeeper started")

        # ------------------------------------
        # Phase 1: Redis-driven cleanup
        # ------------------------------------
        for key in redis_conn.scan_iter("*"):
            try:
                job = redis_conn.hgetall(key)
                cleanup_at = job.get("cleanup_at")

                if not cleanup_at:
                    continue

                if int(cleanup_at) <= now:
                    job_dir = os.path.join(TMP_DIR, key)

                    if os.path.exists(job_dir):
                        shutil.rmtree(job_dir)

                    redis_conn.delete(key)
                    print(f"✅ Cleaned job {key}")

            except Exception as e:
                print(f"⚠️ Error cleaning job {key}: {e}")

        # ------------------------------------
        # Phase 2: Orphan directory cleanup
        # (if Redis lost data, crash, etc)
        # ------------------------------------
        orphan_cutoff = now - (24 * 3600)   # 24 hours

        for folder in os.listdir(TMP_DIR):
            if folder == ".gitkeep":
                continue

            path = os.path.join(TMP_DIR, folder)

            if not os.path.isdir(path):
                continue

            try:
                created = os.path.getctime(path)

                if created < orphan_cutoff:
                    shutil.rmtree(path)
                    print(f"🔥 Removed orphaned folder: {folder}")

            except Exception as e:
                print(f"⚠️ Failed removing orphan {folder}: {e}")

        print("✅ Housekeeper finished\n")

