from redis import Redis
import os

redis_conn = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

class ApplicationJob:
    def set_status(self, job_id, status, progress=None):
        if progress is not None:
            redis_conn.hset(job_id, mapping={
                "status": status,
                "progress": progress
            })
        else:
            redis_conn.hset(job_id, "status", status)

    def get_status(self, job_id):
        return redis_conn.hgetall(job_id)

    def expire(self, job_id, seconds=3600):
        redis_conn.expire(job_id, seconds)

    def delete(self, job_id):
        redis.delete(job_id)
