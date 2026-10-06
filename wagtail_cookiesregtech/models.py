from django.db import models

from . import DEFAULT_SERVER


class Settings(models.Model):
    """Singleton row holding the CookiesRegTech connection."""

    server = models.URLField(default=DEFAULT_SERVER)
    domain_id = models.CharField(max_length=40, blank=True, default="")
    secret = models.CharField(max_length=64, blank=True, default="")
    pending_token = models.CharField(max_length=64, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    banner_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "CookiesRegTech settings"
        verbose_name_plural = "CookiesRegTech settings"

    def __str__(self):
        return "CookiesRegTech settings"

    @classmethod
    def load(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance

    @property
    def server_url(self):
        return (self.server or DEFAULT_SERVER).rstrip("/")
