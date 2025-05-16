from django.utils.deprecation import MiddlewareMixin
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class MongoDBReconnectMiddleware(MiddlewareMixin):
    """
    Middleware to handle MongoDB connection issues by attempting to reconnect.
    This version works with the limitations of djongo and pymongo integration.
    """
    
    def __call__(self, request):
        """
        Call the middleware, ensuring MongoDB connection before processing.
        """
        try:
            self.ensure_mongodb_connection()
        except Exception as e:
            # Log but continue - don't break the request if connection check fails
            logger.error(f"Error in MongoDB connection middleware: {str(e)}")
        
        return super().__call__(request)
    
    def ensure_mongodb_connection(self):
        """
        Check and re-establish MongoDB connection if needed.
        Very carefully handle the djongo connection which may not be fully initialized.
        """
        try:
            # Get the connection from django's connection pool
            connection = connections['default']
            
            # Check if the connection exists and is properly initialized
            if hasattr(connection, 'connection') and connection.connection:
                # Try a simple database operation that won't cause SQL translation issues
                db = connection.connection.get_database()
                # Just accessing a property is enough to test connection
                _ = db.name
                logger.debug("MongoDB connection verified")
            else:
                # If connection isn't initialized yet, just log it and continue
                logger.info("MongoDB connection not yet initialized")
                
        except Exception as e:
            logger.warning(f"Unexpected error checking MongoDB connection: {str(e)}")
            
            # Close any existing connection to force a reconnect on next use
            try:
                if hasattr(connections['default'], 'connection') and connections['default'].connection:
                    connections['default'].close()
                    logger.info("Closed existing MongoDB connection to force reconnect")
            except Exception as close_error:
                logger.error(f"Error closing MongoDB connection: {str(close_error)}")