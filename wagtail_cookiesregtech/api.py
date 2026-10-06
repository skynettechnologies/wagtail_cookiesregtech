"""CookiesRegTech plugin API client (standard library only)."""

import json
import urllib.error
import urllib.request

from . import VERSION


def post(server, path, payload):
    """POST JSON. Returns the decoded body with `_status` added.

    Explicit Accept and User-Agent headers keep strict firewalls from
    mistaking the request for a bot.
    """
    request = urllib.request.Request(
        server.rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CookiesRegTech-Wagtail/%s (+https://www.cookiesregtech.com)" % VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        raw = error.read()
        status = error.code
    except Exception as error:  # noqa: BLE001 - surfaced to the admin as a message
        return {"_status": 0, "_error": str(error)}

    try:
        body = json.loads(raw.decode("utf-8"))
    except ValueError:
        body = {}

    if not isinstance(body, dict):
        body = {}
    body["_status"] = status
    return body


def unexpected_reply(result):
    if not result.get("_status") and result.get("_error"):
        return "Could not reach the consent server: %s" % result["_error"]

    return (
        "Unexpected reply from the consent server (HTTP %d). "
        "If this repeats, the request may be blocked by a firewall." % int(result.get("_status") or 0)
    )
