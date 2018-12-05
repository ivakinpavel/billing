from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = 'billing.core'
    verbose_name = "Core"

    def ready(self):
        try:
            import core.signals  # noqa F401
        except ImportError:
            pass
