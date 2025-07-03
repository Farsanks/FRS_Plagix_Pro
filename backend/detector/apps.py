from django.apps import AppConfig

class DetectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.detector'

    def ready(self):
        import backend.detector.signals  # <-- Make sure this line is added
