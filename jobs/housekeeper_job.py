import os
import shutil
import time
from jobs import redis_conn
from services.openlp_service import TMP_DIR


class HousekeeperJob:
    """
    Cleans old jobs:
    - If Redis says job should expire → delete folder + Redis key
    - If folder is old but Redis key still exists → delete both
    - If folder is old and Redis key missing → delete folder only
    """

    PREFIX = "openlp:job:"

    def __init__(self, max_age=60):
        self.max_age = max_age  # seconds

    def run(self):
        now = int(time.time())
        cutoff = now - self.max_age

        print("\n🧹 Housekeeper started")
        print(f"⏰ Expiring jobs older than {self.max_age} seconds\n")

        self._cleanup_redis_jobs(now)
        self._cleanup_orphan_dirs(cutoff)

        print("✅ Housekeeper finished\n")

    def _cleanup_redis_jobs(self, now):
        for key in redis_conn.scan_iter(f"{self.PREFIX}*"):

            try:
                job = redis_conn.hgetall(key)

                if not job:
                    continue

                cleanup_at = job.get("cleanup_at")
                if cleanup_at is None:
                    continue   # Not downloaded yet OR intentionally unset

                if int(cleanup_at) <= now:
                    self._delete_job(key)

            except Exception as e:
                print(f"⚠️ Redis cleanup failed for {key}: {e}")

    def _cleanup_orphan_dirs(self, cutoff):
        for folder in os.listdir(TMP_DIR):

            if folder.startswith("."):
                continue

            path = os.path.join(TMP_DIR, folder)
            if not os.path.isdir(path):
                continue

            try:
                modified = int(os.path.getmtime(path))

                if modified < cutoff:
                    # Orphan cleanup
                    self._delete_path(path, folder)

                    # Also delete Redis key if it exists
                    redis_key = f"{self.PREFIX}{folder}"
                    if redis_conn.exists(redis_key):
                        redis_conn.delete(redis_key)
                        print(f"🗑️ Removed orphan Redis key: {redis_key}")

            except Exception as e:
                print(f"⚠️ Orphan cleanup failed for {folder}: {e}")

    def _delete_job(self, key):
        job_id = key.split(self.PREFIX, 1)[1]
        path = os.path.join(TMP_DIR, job_id)

        self._delete_path(path, job_id)
        redis_conn.delete(key)

        print(f"✅ Deleted Redis + folder: {key}")

    def _delete_path(self, path, label=None):
        try:
            shutil.rmtree(path, ignore_errors=True)
            print(f"🔥 Deleted folder: {label}")
        except Exception as e:
            print(f"❌ Failed deleting {label}: {e}")

