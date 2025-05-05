import logging
import os
import random
import threading
import time
from redis import Redis
import requests
from flask import Flask, Response

DEBUG = os.environ.get("DEBUG", "").lower().startswith("y")

log = logging.getLogger(__name__)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)

pause_worker = threading.Event()

redis = Redis("redis")
app = Flask(__name__)


def get_random_bytes():
    r = requests.get("http://rng/32")
    return r.content


def hash_bytes(data):
    r = requests.post("http://hasher/",
                      data=data,
                      headers={"Content-Type": "application/octet-stream"})
    hex_hash = r.text
    return hex_hash


@app.route('/')
def index():
    log.info("Received request from co-worker. Pausing worker")
    pause_worker.set()
    return Response("OK", mimetype="text/plain")


def work_loop(interval=1):
    deadline = 0
    loops_done = 0
    while True:
        if pause_worker.is_set():
            log.info("Worker paused. Going to sleep...")
            # Sleep for a random time
            sleep_time = random.uniform(0.2, 0.4)
            log.debug(f"Sleeping for {sleep_time:.3f} seconds")
            time.sleep(sleep_time)
            
            # Reset the flag
            pause_worker.clear()
            log.info("Worker resuming operation")
        
        if time.time() > deadline:
            log.info("{} more units of work done, updating hash counter"
                     .format(loops_done))
            redis.incrby("hashes", loops_done)
            loops_done = 0
            deadline = time.time() + interval
        
        work_once()
        loops_done += 1


def work_once():
    log.debug("Doing one unit of work")
    time.sleep(0.1)
    random_bytes = get_random_bytes()
    hex_hash = hash_bytes(random_bytes)
    if not hex_hash.startswith('0'):
        log.debug("No coin found")
        return
    log.info("Coin found: {}...".format(hex_hash[:8]))
    created = redis.hset("wallet", hex_hash, random_bytes)
    if not created:
        log.info("We already had that coin")


def start_worker_thread():
    """Start the worker thread that performs the mining operations"""
    worker_thread = threading.Thread(target=worker_main, daemon=True)
    worker_thread.start()
    return worker_thread


def worker_main():
    """Main function for the worker thread"""
    while True:
        try:
            work_loop()
        except Exception:
            log.exception("In work loop:")
            log.error("Waiting 10s and restarting.")
            time.sleep(10)


if __name__ == "__main__":
    # Start the worker thread in the background
    worker_thread = start_worker_thread()
    log.info("Worker thread started")
    
    # Run the Flask app in the main thread
    log.info("Starting Flask app")
    app.run(host="0.0.0.0", port=80, threaded=True)


