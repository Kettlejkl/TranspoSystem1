from django.core.management.base import BaseCommand
from django.db import connections
import pymongo
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Keepalive command to periodically check and maintain MongoDB connection'
    
    def handle(self, *args, **options):
        """
        Command to run as a scheduled task to keep the MongoDB connection alive.
        Performs regular health checks and reconnects if needed.
        """
        self.stdout.write('Starting MongoDB keepalive service...')
        
        check_interval = 60  # Check every minute
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        backoff_factor = 2
        
        while True:
            try:
                self.check_mongodb_connection()
                self.stdout.write(self.style.SUCCESS(f'✓ MongoDB connection verified at {time.strftime("%H:%M:%S")}'))
                # Reset reconnect attempts counter on success
                reconnect_attempts = 0
                
            except Exception as e:
                reconnect_attempts += 1
                backoff_time = min(30, (backoff_factor ** reconnect_attempts) * 0.5)
                
                self.stdout.write(
                    self.style.ERROR(f'✗ MongoDB connection error: {str(e)}. '
                                    f'Attempt {reconnect_attempts}/{max_reconnect_attempts}')
                )
                
                if reconnect_attempts >= max_reconnect_attempts:
                    self.stdout.write(
                        self.style.WARNING('Maximum reconnection attempts reached. Resetting counter...')
                    )
                    reconnect_attempts = 0
                
                # Force reconnection
                self.force_reconnect()
                time.sleep(backoff_time)  # Wait before next check
            
            # Sleep until next check
            time.sleep(check_interval)
    
    def check_mongodb_connection(self):
        """
        Verify MongoDB connection is working properly.
        """
        connection = connections['default']
        
        # For djongo, access the pymongo client
        if hasattr(connection, 'connection') and connection.connection:
            # Use the MongoDB command API to test the connection
            db = connection.connection.get_database()
            result = db.command('ping')
            
            if result.get('ok') != 1:
                raise pymongo.errors.ConnectionFailure("MongoDB ping command failed")
            
            # Also check server info as another verification
            _ = connection.connection.server_info()
        else:
            # Connection not initialized, initialize it
            cursor = connection.cursor()
            cursor.close()
    
    def force_reconnect(self):
        """
        Force a reconnection to MongoDB by closing existing connections.
        """
        try:
            # Close the connection at Django level
            if connections['default'].connection:
                connections['default'].close()
                self.stdout.write('Closed existing MongoDB connection')
            
            # Ensure we get a fresh connection
            connection = connections['default']
            connection.ensure_connection()
            
            # Verify the new connection works
            db = connection.connection.get_database()
            result = db.command('ping')
            
            if result.get('ok') == 1:
                self.stdout.write(self.style.SUCCESS('Successfully reconnected to MongoDB'))
            else:
                self.stdout.write(self.style.ERROR('Reconnection failed: MongoDB ping test unsuccessful'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during MongoDB reconnection: {str(e)}'))