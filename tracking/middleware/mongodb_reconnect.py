from django.utils.deprecation import MiddlewareMixin
from django.db import connections
from django.core.signals import request_finished
from django.dispatch import receiver
import pymongo
import logging
import time

logger = logging.getLogger(__name__)

class MongoDBReconnectMiddleware(MiddlewareMixin):
    """
    Enhanced middleware to handle MongoDB connection issues by proactively
    checking connections and implementing smart reconnection logic.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.connection_check_interval = 300  # Check connection every 5 minutes
        self.last_check_time = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.backoff_factor = 2  # Exponential backoff factor
    
    def __call__(self, request):
        """
        Call the middleware, ensuring MongoDB connection before processing.
        Uses time-based checking to avoid excessive connection tests.
        """
        current_time = time.time()
        
        # Only check connection if enough time has passed since last check
        if current_time - self.last_check_time > self.connection_check_interval:
            self.last_check_time = current_time
            try:
                self.ensure_mongodb_connection()
                # Reset reconnect attempts on successful connection
                self.reconnect_attempts = 0
            except Exception as e:
                logger.error(f"MongoDB connection error in middleware: {str(e)}")
                # Increment reconnect attempts, but don't exceed max
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    self.reconnect_attempts += 1
        
        try:
            # Process the request
            response = self.get_response(request)
            return response
        except pymongo.errors.PyMongoError as e:
            # Catch MongoDB errors that might occur during request processing
            logger.error(f"MongoDB error during request: {str(e)}")
            self.force_reconnect()
            # Re-raise the exception to let Django handle it appropriately
            raise
    
    def ensure_mongodb_connection(self):
        """
        Check and re-establish MongoDB connection if needed.
        Uses enhanced error handling specific to pymongo errors.
        """
        try:
            # Get the connection from django's connection pool
            connection = connections['default']
            
            # For djongo, we need to access the pymongo client
            if hasattr(connection, 'connection') and connection.connection:
                # Try a simple database operation to verify connection
                db = connection.connection.get_database()
                # Execute a simple command to truly test the connection
                db.command('ping')
                logger.debug("MongoDB connection verified successfully")
            else:
                logger.info("MongoDB connection not yet initialized, initializing now")
                # Force initialization of connection
                _ = connection.cursor()
                
        except pymongo.errors.AutoReconnect as e:
            logger.warning(f"MongoDB AutoReconnect error: {str(e)}")
            self.handle_reconnect()
            
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logger.warning(f"MongoDB ServerSelectionTimeoutError: {str(e)}")
            self.handle_reconnect()
            
        except pymongo.errors.ConnectionFailure as e:
            logger.warning(f"MongoDB ConnectionFailure: {str(e)}")
            self.handle_reconnect()
            
        except pymongo.errors.NetworkTimeout as e:
            logger.warning(f"MongoDB NetworkTimeout: {str(e)}")
            self.handle_reconnect()
            
        except pymongo.errors.InvalidOperation as e:
            logger.warning(f"MongoDB InvalidOperation: {str(e)}")
            if "MongoClient after close" in str(e):
                self.force_reconnect()
                
        except Exception as e:
            logger.error(f"Unexpected error checking MongoDB connection: {str(e)}")
            self.handle_reconnect()
    
    def handle_reconnect(self):
        """
        Handle reconnection with exponential backoff.
        """
        # Calculate backoff time based on number of reconnect attempts
        backoff_time = (self.backoff_factor ** self.reconnect_attempts) * 0.5
        if backoff_time > 30:  # Cap at 30 seconds max
            backoff_time = 30
            
        logger.info(f"Reconnecting to MongoDB after {backoff_time} seconds delay (attempt {self.reconnect_attempts + 1})")
        time.sleep(backoff_time)
        self.force_reconnect()
    
    def force_reconnect(self):
        """
        Force reconnection by closing existing connections.
        """
        try:
            # Close the connection to force Django to create a new one on next use
            if connections['default'].connection:
                # Close at the Django level
                connections['default'].close()
                logger.info("Closed existing MongoDB connection to force reconnect")
                
                # Also ensure the pymongo client is properly closed
                client = getattr(connections['default'], '_client', None)
                if client:
                    client.close()
                    logger.info("Closed pymongo client")
            
            # Try to establish new connection immediately
            connections['default'].ensure_connection()
            logger.info("Reconnected to MongoDB successfully")
            
        except Exception as close_error:
            logger.error(f"Error during MongoDB reconnection: {str(close_error)}")


@receiver(request_finished)
def check_mongodb_connection_after_request(sender, **kwargs):
    """
    Signal handler to check MongoDB connection after each request.
    This provides an additional safety net to catch connection issues.
    """
    try:
        # Check if the connection exists and needs to be verified
        if 'default' in connections and connections['default'].connection:
            # Simple check to see if we need to reset the connection
            try:
                client = getattr(connections['default'], '_client', None)
                if client and hasattr(client, 'server_info'):
                    # Just try to access a property to test connection
                    _ = client.address
            except (pymongo.errors.InvalidOperation, pymongo.errors.ServerSelectionTimeoutError):
                logger.info("MongoDB connection issue detected after request - closing connection")
                connections['default'].close()
    except Exception as e:
        logger.error(f"Error in MongoDB post-request check: {str(e)}")