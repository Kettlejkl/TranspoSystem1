from django.db import connections
from pymongo.errors import AutoReconnect, ConnectionFailure, NetworkTimeout, InvalidOperation
import time
import logging

logger = logging.getLogger(__name__)

class MongoDBReconnectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to ensure MongoDB connection before processing the request
        self.ensure_mongodb_connection()
        
        try:
            response = self.get_response(request)
            return response
        except (AutoReconnect, ConnectionFailure, NetworkTimeout, InvalidOperation) as e:
            # If we encounter a connection error during request processing
            logger.warning(f"MongoDB connection error during request: {e}")
            # Try to reconnect
            self.ensure_mongodb_connection()
            # Retry the request one more time
            response = self.get_response(request)
            return response
    
    def ensure_mongodb_connection(self):
        """Ensure MongoDB connection is alive or reconnect"""
        max_retries = 3
        retry_delay = 1  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                # Get the MongoDB connection
                connection = connections['default']
                # Try a simple query to test the connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return  # Connection is working
            except (AutoReconnect, ConnectionFailure, NetworkTimeout, InvalidOperation) as e:
                logger.warning(f"MongoDB connection error (attempt {attempt+1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Add exponential backoff
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying connection in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    # Try to close and then recreate the connection
                    try:
                        connections.close_all()
                    except Exception as close_err:
                        logger.warning(f"Error closing connections: {close_err}")
                else:
                    logger.error("Failed to reconnect to MongoDB after multiple attempts")