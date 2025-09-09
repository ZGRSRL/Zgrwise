#!/usr/bin/env python3
"""
Main worker entry point with RQ queues and scheduler
"""

import logging
import os
import sys
from redis import Redis
from rq import Queue, Worker, Connection
from rq.worker import HerokuWorker as Worker
import threading
from .scheduler import setup_scheduler, run_scheduler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_conn = Redis.from_url(redis_url)

# Create RQ queues
queues = {
    'rss': Queue('rss', connection=redis_conn),
    'ingest': Queue('ingest', connection=redis_conn),
    'embed': Queue('embed', connection=redis_conn),
    'export': Queue('export', connection=redis_conn),
    'review': Queue('review', connection=redis_conn),
    'ai': Queue('ai', connection=redis_conn)
}

def start_worker(queue_name: str):
    """Start a worker for a specific queue"""
    try:
        with Connection(redis_conn):
            worker = Worker([queues[queue_name]])
            logger.info(f"Starting worker for queue: {queue_name}")
            worker.work()
    except Exception as e:
        logger.error(f"Error in worker {queue_name}: {e}")


def start_scheduler():
    """Start the scheduler in a separate thread"""
    try:
        setup_scheduler()
        run_scheduler()
    except Exception as e:
        logger.error(f"Error in scheduler: {e}")


def main():
    """Main entry point"""
    logger.info("Starting ZgrWise Worker...")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler started in background")
    
    # Start workers for each queue
    worker_threads = []
    
    for queue_name in queues.keys():
        worker_thread = threading.Thread(
            target=start_worker, 
            args=(queue_name,),
            daemon=True
        )
        worker_thread.start()
        worker_threads.append(worker_thread)
        logger.info(f"Worker thread started for {queue_name}")
    
    # Wait for all workers
    try:
        for thread in worker_threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("Shutting down workers...")
        sys.exit(0)


if __name__ == "__main__":
    main() 