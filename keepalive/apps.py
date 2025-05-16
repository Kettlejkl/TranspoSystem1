from django.apps import AppConfig
import threading
import time
import requests
import logging
import os

logger = logging.getLogger(__name__)

class KeepaliveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keepalive'
    
    def ready(self):
        """
        This method is called when Django starts.
        We'll use it to start our keep-alive thread.
        """
        # Django runs this method twice in development mode
        # We use RUN_MAIN to ensure we only run our code once
        run_main = os.environ.get('RUN_MAIN')
        
        # Only run in the main process or when RUN_MAIN is not set (in production)
        if run_main == 'true' or run_main is None:
            # Only run in production mode
            from django.conf import settings
            if not settings.DEBUG:
                self._start_keepalive_thread()
    
    def _start_keepalive_thread(self):
        """Start the keep-alive thread in a separate thread"""
        def keepalive_worker():
            """Worker function that pings the app periodically"""
            app_url = os.environ.get('APP_URL', 'https://transposystem.onrender.com')
            ping_url = f"{app_url}/keepalive/ping/"
            
            logger.info("Starting keep-alive service")
            
            while True:
                try:
                    logger.info("Sending keep-alive request")
                    response = requests.get(ping_url, timeout=30)
                    status = response.status_code
                    logger.info(f"Keep-alive response: HTTP {status}")
                except Exception as e:
                    logger.error(f"Keep-alive request failed: {e}")
                
                # Sleep for 14 minutes (840 seconds)
                # This is just under Render's 15-minute inactivity threshold
                time.sleep(840)
        
        # Create and start the thread
        keep_alive_thread = threading.Thread(target=keepalive_worker, daemon=True)
        keep_alive_thread.name = "KeepAliveThread"
        keep_alive_thread.start()
        logger.info("Keep-alive thread started successfully")