import requests
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def main():
    log.info("Co-worker service starting")
    
    while True:
        try:
            sleep_time = random.uniform(0.5, 1.5)
            log.info(f"Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
            log.info("Sending GET request to worker")
            response = requests.get("http://worker/")
            
            log.info(f"Worker responded with status: {response.status_code}, body: '{response.text}'")

        except requests.exceptions.RequestException as e:
            log.error(f"Error connecting to worker: {e}")
        except Exception as e:
            log.exception(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()