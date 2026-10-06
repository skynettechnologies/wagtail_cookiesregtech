"""Injects the consent bootstrap right after <head> on front-end pages.

Head-first matters: the consent script must run before analytics and tag
managers to block trackers and signal Google Consent Mode in time — which
is why this rewrites <head> instead of appending before </body>."""

import re

from django.db import DatabaseError
from django.urls import NoReverseMatch, reverse

from .models import Settings

# `<head>` or `<head attr...>`, but never `<header>` / `<headline>`.
HEAD_RE = re.compile(rb"<head(?:\s[^>]*)?>", re.IGNORECASE)
DOMAIN_RE = re.compile(r"^[a-z0-9]{10,40}$", re.IGNORECASE)

STATIC_PREFIXES = ("/django-admin/", "/static/", "/media/")


def admin_prefixes():
    """The Wagtail admin may be mounted anywhere (/admin/, /cms/, ...), so
    ask the URL resolver instead of assuming /admin."""
    prefixes = list(STATIC_PREFIXES) + ["/admin/"]

    try:
        prefixes.append(reverse("wagtailadmin_home"))
    except NoReverseMatch:  # pragma: no cover - admin not installed
        pass

    return tuple(set(prefixes))


class BannerInjectionMiddleware:
    """Add to MIDDLEWARE. Skips the admin, non-HTML, compressed and streaming responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path or ""

        # Trailing slash added so "/administration/" (a normal page) is not mistaken for "/admin/".
        if any((path + "/").startswith(prefix) for prefix in admin_prefixes()):
            return response

        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match is not None:
            app_names = getattr(resolver_match, "app_names", None) or []
            if "wagtailadmin" in app_names or "wagtail_cookiesregtech" in app_names:
                return response

        if getattr(response, "streaming", False):
            return response
        if "text/html" not in response.get("Content-Type", ""):
            return response
        # Already compressed (e.g. GZipMiddleware ran first): rewriting the bytes would corrupt the body.
        if response.get("Content-Encoding"):
            return response

        try:
            # Read-only: never write to the database while serving a visitor's page view.
            settings = Settings.objects.filter(pk=1).first()
        except DatabaseError:  # e.g. migrations not applied yet
            return response

        if settings is None or not settings.banner_enabled:
            return response

        domain_id = (settings.domain_id or "").strip()

        if not domain_id or not DOMAIN_RE.match(domain_id):
            return response

        src = "%s/embed/boot/%s.js" % (settings.server_url, domain_id)
        tag = ('<script src="%s"></script>' % src).encode("utf-8")
        # First occurrence only: the bootstrap must be the first script in head.
        response.content = HEAD_RE.sub(lambda match: match.group(0) + tag, response.content, count=1)

        if response.has_header("Content-Length"):
            response["Content-Length"] = str(len(response.content))

        return response
