from django.apps import AppConfig

class UtilityConfig(AppConfig):
    name = 'utility'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_default_site_settings, sender=self)


def create_default_site_settings(sender, **kwargs):
    from utility.models import SiteSettings
    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(
            siteName="BD-Pay",
            siteFavIconLink="https://chatgpt.com/favicon.ico",
            siteLink="http://127.0.0.1:8000",
            uUid="1000",
        )
