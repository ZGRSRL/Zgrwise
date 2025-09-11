import os, redis
from rq import Worker, Queue, Connection

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
listen = ["default","rss"]

if __name__ == "__main__":
    conn = redis.from_url(redis_url)
    with Connection(conn):
        worker = Worker([Queue(n) for n in listen])
        worker.work(with_scheduler=True)