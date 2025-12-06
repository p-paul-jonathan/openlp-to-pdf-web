from rq import Worker, Queue, Connection
from jobs import redis_conn

if __name__ == "__main__":
    print("🚀 Starting OpenLP RQ Worker...")

    # Connect to Redis and listen on the openlp-jobs queue
    with Connection(redis_conn):
        worker = Worker(["openlp-jobs"])
        worker.work(with_scheduler=False)
