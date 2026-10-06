from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _

try:
    # Wagtail >= 3.0
    from wagtail import hooks
except ImportError:  # pragma: no cover - older Wagtail
    from wagtail.core import hooks

from wagtail.admin.menu import MenuItem

from . import urls as crt_urls


@hooks.register("register_admin_urls")
def register_admin_urls():
    """Mounts the page under the Wagtail admin, e.g. /admin/cookiesregtech/."""
    return [
        path(
            "cookiesregtech/",
            include((crt_urls, "wagtail_cookiesregtech"), namespace="wagtail_cookiesregtech"),
        ),
    ]


@hooks.register("register_icons")
def register_icons(icons):
    return icons + ["wagtail_cookiesregtech/icons/cookiesregtech.svg"]


class CookiesRegTechMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.is_active and request.user.has_perm("wagtailadmin.access_admin")


@hooks.register("register_admin_menu_item")
def register_cookiesregtech_menu_item():
    """A top-level sidebar entry (next to Reports and the other apps), not a
    child of Settings. Order 9100 sits right after Reports (9000) and before
    Settings (10000)."""
    return CookiesRegTechMenuItem(
        _("CookiesRegTech"),
        reverse("wagtail_cookiesregtech:settings"),
        name="cookiesregtech",
        icon_name="cookiesregtech",
        order=9100,
    )
