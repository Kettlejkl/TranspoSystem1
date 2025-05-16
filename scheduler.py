# scheduler.py
import time
import os
import requests
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('keep_alive')

def keep_alive():
    """Send a request to the keep-alive endpoint every 14 minutes"""
    app_url = os.getenv('APP_URL', 'https://transposystem.onrender.com')
    ping_url = f"{app_url}/keepalive/ping/"
    
    while True:
        try:
            logger.info("Sending keep-alive request...")
            response = requests.get(ping_url, timeout=30)
            if response.status_code == 200:
                logger.info("Keep-alive successful")
            else:
                logger.warning(f"Keep-alive request returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive request failed: {e}")
        
        # Sleep for 14 minutes (840 seconds) - just under Render's 15-minute sleep threshold
        time.sleep(840)

# Start the keep-alive thread when this module is imported
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()