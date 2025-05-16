from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect
import logging

logger = logging.getLogger(__name__)

class MongoDBReconnectMiddleware(MiddlewareMixin):
    """
    Middleware to handle MongoDB connection issues by attempting to reconnect.
    """
    
    def __call__(self, request):
        """
        Call the middleware, ensuring MongoDB connection before processing.
        """
        self.ensure_mongodb_connection()
        return super().__call__(request)
    
    def ensure_mongodb_connection(self):
        """
        Check and re-establish MongoDB connection if needed.
        Using proper MongoDB methods instead of SQL commands.
        """
        try:
            # Get the pymongo client directly from the Django connection
            client = connection.connection.client
            
            # Use a simple command to test the connection
            client.admin.command('ping')
            
            logger.debug("MongoDB connection verified")
            
        except (ServerSelectionTimeoutError, AutoReconnect) as e:
            logger.warning(f"MongoDB connection issue detected: {str(e)}")
            
            # Close the connection to force a reconnect on next use
            if hasattr(connection, 'connection') and connection.connection:
                connection.close()
                logger.info("Closed existing MongoDB connection to force reconnect")
                
        except Exception as e:
            logger.error(f"Unexpected error checking MongoDB connection: {str(e)}")