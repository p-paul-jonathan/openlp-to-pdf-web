import os
import traceback
import time
from jobs import redis_conn
from services.openlp_service import extract_openlp_items, extract_service_items, TMP_DIR
from services.pdf_service import convert_slides_to_pdf

class UploaderJob:
    def set_status(self, job_id, status, progress=None):
        if progress is not None:
            redis_conn.hset(f"openlp:job:{job_id}", mapping={
                "status": status,
                "progress": progress,
                "cleanup_at": int(time.time() + 600)
            })
        else:
            redis_conn.hset(f"openlp:job:{job_id}", "status", status)

    def get_status(self, job_id):
        return redis_conn.hgetall(f"openlp:job:{job_id}")

    def expire(self, job_id, seconds=3600):
        redis_conn.expire(f"openlp:job:{job_id}", seconds)

    def delete(self, job_id):
        redis_conn.delete(f"openlp:job:{job_id}")

    def run(self, job_id, data):
        job_dir = os.path.join(TMP_DIR, job_id)

        try:
            # -----------------------------
            # Upload phase
            # -----------------------------
            self.set_status(job_id, "in_progress", "Uploading")

            service_file_path = data["service_file_path"]
            theme_file_path = data["theme_file_path"]

            # -----------------------------
            # Processing phase
            # -----------------------------
            self.set_status(job_id, "in_progress", "Processing")

            service_extract_dir, theme_extract_dir = extract_openlp_items(
                job_dir,
                service_file_path,
                theme_file_path
            )

            # -----------------------------
            # Conversion phase
            # -----------------------------
            self.set_status(job_id, "in_progress", "Converting")

            slides = extract_service_items(service_extract_dir)

            pdf_path = convert_slides_to_pdf(
                slides,
                theme_extract_dir,
                job_dir
            )

            # -----------------------------
            # Done
            # -----------------------------
            self.set_status(job_id, "completed", None)

            return pdf_path

        except Exception as e:
            # -----------------------------
            # Failure handling
            # -----------------------------
            error_msg = f"{type(e).__name__}: {str(e)}"

            print("\n❌ JOB FAILED:", job_id)
            print(error_msg)
            traceback.print_exc()

            self.set_status(job_id, "error", error_msg)

            return None
