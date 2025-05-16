from django.http import JsonResponse
from django.db import connections
import logging

logger = logging.getLogger(__name__)

def ping(request):
    """
    Simple endpoint that returns a 200 response to keep the app alive
    Also verifies database connection as a health check
    """
    try:
        # Try to access the database as part of the health check
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            db_status = "connected" if result and result[0] == 1 else "error"
    except Exception as e:
        logger.warning(f"Database check failed during ping: {e}")
        db_status = "error"
    
    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "message": "Application is running"
    })