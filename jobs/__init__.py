from redis import Redis
from rq import Queue

redis_conn = Redis(host="localhost", port=6379)
queue = Queue("openlp-jobs", connection=redis_conn)


def enqueue(job_class, job_id, data):
    job_class().set_status(job_id, "queued", 0)
    return queue.enqueue(job_class().run, job_id, data)

def get_job_status(job_class, job_id):
    try:
        job = job_class().fetch(job_id, connection=redis_conn)
        return {
            "status": job.get_status(),
            "result": job.result,
            "failed": job.is_failed,
            "started_at": job.started_at,
            "ended_at": job.ended_at
        }
    except Exception:
        return {"status": "not_found"}
