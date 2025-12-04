import os
from flask import render_template, jsonify, send_file
from services.openlp_service import TMP_DIR
import time
from jobs import get_job, redis_conn


def get_job_status(job_id):
    return render_template("job.html", job_id=job_id)


def get_job_json(job_id):
    job = get_job(job_id)

    if not job:
        return jsonify({"status": "not_found"})

    return jsonify(job)


def download_pdf(job_id):
    pdf_path = os.path.join(TMP_DIR, job_id, "slides.pdf")

    if not os.path.exists(pdf_path):
        return "PDF not available", 404

    # ✅ Store cleanup schedule (10 minutes from now)
    cleanup_at = int(time.time() + 600)

    redis_conn.hset(job_id, mapping={
        "cleanup_at": cleanup_at
    })

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="slides.pdf"
    )
