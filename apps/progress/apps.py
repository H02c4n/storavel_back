from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.progress"  # kendi app path'ine göre düzelt

    def ready(self):
        import apps.progress.signals  # noqa