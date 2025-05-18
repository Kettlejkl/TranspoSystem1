# tracking/apps.py

from django.apps import AppConfig

class TrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracking'

    def ready(self):
        """Import signals when the app is ready"""
        import tracking.models_signals  # Import the signals module