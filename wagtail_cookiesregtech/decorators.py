"""Wagtail gates admin views behind "wagtailadmin.access_admin" rather
than Django's is_staff flag; this decorator mirrors that convention."""
from functools import wraps

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def wagtail_admin_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), getattr(settings, "LOGIN_URL", None))
        if not request.user.has_perm("wagtailadmin.access_admin"):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper
