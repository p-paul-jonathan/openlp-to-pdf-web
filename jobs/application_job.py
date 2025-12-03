import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

class ApplicationJob:
    def set_status(self, job_id, status, progress=None):
        if progress is not None:
            r.hset(job_id, mapping={
                "status": status,
                "progress": progress
            })
        else:
            r.hset(job_id, "status", status)
    def get_status(self, job_id):
        return r.hgetall(job_id)

    def expire(self, job_id, seconds=3600):
        r.expire(job_id, seconds)
