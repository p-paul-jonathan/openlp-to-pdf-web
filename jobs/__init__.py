from redis import Redis
import os
from rq import Queue

redis_conn = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

queue = Queue("openlp-jobs", connection=redis_conn)


def enqueue(job_class, job_id, payload):
    job = job_class()
    job.set_status(job_id, "queued", "Waiting")
    return queue.enqueue(job.run, job_id, payload)


def get_job(job_id):
    data = redis_conn.hgetall(f"openlp:job:{job_id}")
    if not data:
        return None
    return data

def delete_job(job_id):
    redis_conn.delete(f"openlp:job:{job_id}")
