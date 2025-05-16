# scheduler.py
import time
import os
import requests
import threading
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('keep_alive')

def keep_alive():
    """Send a request to the keep-alive endpoint every 14 minutes with slight jitter"""
    app_url = os.getenv('APP_URL', 'https://transposystem.onrender.com')
    ping_url = f"{app_url}/keepalive/ping/"
    
    # Track consecutive failures
    consecutive_failures = 0
    
    while True:
        try:
            logger.info("Sending keep-alive request...")
            response = requests.get(ping_url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Keep-alive successful: {response.text[:50]}...")
                consecutive_failures = 0  # Reset counter on success
            else:
                consecutive_failures += 1
                logger.warning(f"Keep-alive request returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            consecutive_failures += 1
            logger.error(f"Keep-alive request failed: {e}")
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Unexpected error in keep-alive: {e}")
            
        # Adjust sleep time if experiencing issues (backoff strategy)
        base_sleep = 840  # 14 minutes in seconds
        
        # Add jitter to prevent potential "thundering herd" problems
        jitter = random.randint(-30, 30)  # ±30 seconds of jitter
        
        # Reduce interval if we've had multiple failures (to retry sooner)
        if consecutive_failures > 3:
            sleep_time = max(300, base_sleep - (consecutive_failures * 60))  # Min 5 minutes
            logger.warning(f"Multiple failures detected. Reducing interval to {sleep_time} seconds")
        else:
            sleep_time = base_sleep + jitter
            
        logger.info(f"Next keep-alive request in {sleep_time} seconds")
        time.sleep(sleep_time)

# Start the keep-alive thread when this module is imported
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True, name="KeepAliveThread")
keep_alive_thread.start()
logger.info("Keep-alive scheduler thread started")