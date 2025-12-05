import os
import shutil
import time
from jobs import redis_conn
from services.openlp_service import TMP_DIR


class HousekeeperJob:
    def __init__(self, max_age=60):
        self.max_age = max_age   # seconds


    PREFIX = "openlp:job:"


    # -----------------------------------
    # MAIN CLEANUP LOOP
    # -----------------------------------

    def run(self):
        now = int(time.time())
        cutoff = now - self.max_age

        print("\n🧹 Housekeeper started")
        print(f"⏰ Removing jobs older than {self.max_age} seconds\n")

        # ----------------------------
        # Phase 1: Redis-driven cleanup
        # ----------------------------
        for key in redis_conn.scan_iter(f"{self.PREFIX}*"):
            self._cleanup_redis_job(key, now)

        # ----------------------------
        # Phase 2: Filesystem fallback
        # ----------------------------
        self._cleanup_orphan_dirs(cutoff)

        print("✅ Housekeeper finished\n")


    # -----------------------------------
    # REDIS CLEANUP
    # -----------------------------------

    def _cleanup_redis_job(self, key, now):
        try:
            job = redis_conn.hgetall(key)
            cleanup_at = job.get("cleanup_at")

            if not cleanup_at:
                return

            if int(cleanup_at) <= now:
                self._delete_job(key)

        except Exception as e:
            print(f"⚠️ Redis cleanup failed for {key}: {e}")


    # -----------------------------------
    # FILESYSTEM CLEANUP
    # -----------------------------------

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
                    self._delete_path(path, folder)

            except Exception as e:
                print(f"⚠️ Orphan cleanup failed for {folder}: {e}")


    # -----------------------------------
    # DELETE HELPERS
    # -----------------------------------

    def _delete_job(self, key):
        path = os.path.join(TMP_DIR, key)

        self._delete_path(path, key)
        redis_conn.delete(key)

        print(f"✅ Cleaned Redis + folder: {key}")


    def _delete_path(self, path, label=None):
        try:
            shutil.rmtree(path, ignore_errors=True)
            print(f"🔥 Deleted folder: {label or path}")
        except Exception as e:
            print(f"❌ Failed deleting {label or path}: {e}")
