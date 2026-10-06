"""The CookiesRegTech settings page: connect, pending, connected screens,
mounted under the Wagtail admin by wagtail_hooks.py."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from . import VERSION
from .api import post as api_post
from .api import unexpected_reply
from .decorators import wagtail_admin_access_required
from .models import Settings

CATEGORY_LABELS = {
    "ESSENTIAL": "Essential",
    "FUNCTIONALITY": "Functionality",
    "ANALYTICS": "Analytics",
    "ADS": "Ads",
    "UNCATEGORISED": "Uncategorised",
}


@wagtail_admin_access_required
def settings_page(request):
    settings = Settings.load()

    if request.method == "POST":
        response = handle_action(request, settings)

        if response is not None:
            return response

    state = "connect"
    overview = None
    overview_error = ""

    if settings.secret and settings.domain_id:
        state = "connected"
        result = api_post(settings.server_url, "/api/plugin/overview", {"secret": settings.secret})

        if result.get("_status") == 200:
            overview = result

            for cookie in overview.get("cookies", []):
                cookie["category_label"] = CATEGORY_LABELS.get(cookie.get("category"), cookie.get("category"))
        else:
            overview_error = result.get("error") or result.get("_error") or "HTTP %s" % result.get("_status", 0)
    elif settings.pending_token:
        state = "pending"

    context = {
        "title": "CookiesRegTech",
        "version": VERSION,
        "wagtail_admin_url": reverse("wagtailadmin_home"),
        "settings": settings,
        "state": state,
        "overview": overview,
        "overview_error": overview_error,
        # Resolved here: a filter argument like default:overview.email raises
        # VariableDoesNotExist in templates when overview is None (API unreachable).
        "account_email": settings.email or (overview or {}).get("email") or "",
        "admin_email": getattr(request.user, "email", "") or "",
        "cookies_open": bool(overview) and len(overview.get("cookies", [])) <= 12,
    }

    return render(request, "wagtail_cookiesregtech/settings.html", context)


def handle_action(request, settings):
    action = request.POST.get("crt_action", "")
    back = redirect(reverse("wagtail_cookiesregtech:settings"))

    if action == "connect":
        email = (request.POST.get("email") or "").strip()
        consent = bool(request.POST.get("consent"))

        if "@" not in email or not consent:
            messages.error(request, "Enter a valid email address and accept the terms to continue.")

            return back

        hostname = request.get_host().split(":")[0]
        result = api_post(settings.server_url, "/api/plugin/provision", {
            "email": email,
            "hostname": hostname,
            "platform": "wagtail",
            "consent": True,
        })

        if result.get("status") == "connected":
            settings.domain_id = result["domainId"]
            settings.secret = result["secret"]
            settings.email = result.get("email", email)
            settings.pending_token = ""
            settings.banner_enabled = True
            settings.save()
            messages.success(request, "The free account is ready and the consent banner is live on the site. A sign-in link was emailed to %s." % email)
        elif result.get("status") == "confirmation_sent":
            settings.pending_token = result["requestToken"]
            settings.email = email
            settings.save()
            messages.success(request, 'That email already has an account. We sent it a confirmation link. Click the link, then press "Check status" here.')
        else:
            messages.error(request, result.get("error") or unexpected_reply(result))

        return back

    if action == "check":
        result = api_post(settings.server_url, "/api/plugin/status", {"requestToken": settings.pending_token})

        if result.get("status") == "connected":
            settings.domain_id = result["domainId"]
            settings.secret = result["secret"]
            settings.pending_token = ""
            settings.banner_enabled = True
            settings.save()
            messages.success(request, "Connected. The consent banner is live on this site.")
        elif result.get("status") == "pending":
            messages.warning(request, "Not confirmed yet. Click the link in the email first.")
        else:
            settings.pending_token = ""
            settings.save()
            messages.error(request, result.get("error") or "The request expired. Start again.")

        return back

    if action == "reset":
        settings.pending_token = ""
        settings.save()

        return back

    if action == "save":
        enabled = bool(request.POST.get("banner_enabled"))
        settings.banner_enabled = enabled
        settings.save()
        messages.success(request, "Cookie consent banner is enabled." if enabled else "Cookie consent banner is disabled.")

        return back

    if action in ("dashboard", "upgrade"):
        payload = {"secret": settings.secret}

        if action == "upgrade":
            payload["intent"] = "upgrade"

        result = api_post(settings.server_url, "/api/plugin/login-link", payload)

        if result.get("url"):
            return redirect(result["url"])

        messages.error(request, result.get("error") or "Could not create a sign-in link. Try again.")

        return back

    if action == "disconnect":
        if settings.secret:
            api_post(settings.server_url, "/api/plugin/disconnect", {"secret": settings.secret})

        settings.domain_id = ""
        settings.secret = ""
        settings.pending_token = ""
        settings.email = ""
        settings.save()
        messages.success(request, "Disconnected. The banner is off. The CookiesRegTech account and its data are unchanged.")

        return back

    return None
