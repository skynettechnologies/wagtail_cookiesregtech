

CookiesRegTech shows an accessible cookie consent banner on the website, blocks known trackers until the visitor agrees, signals Google Consent Mode before analytics run, and keeps a consent log that can be exported as proof.

This plugin connects the Wagtail site to a CookiesRegTech account and installs the consent script in the correct position (before analytics and tag managers) automatically — the step most manual installations get wrong.

**Free plan included.** A free account gives a working banner, consent logging, manual cookie scans, layout and color customisation, and 5,000 recorded pageviews per month. Paid plans add scheduled full-site scans, geo-targeted banners, custom CSS, and higher limits — upgrades happen in the CookiesRegTech dashboard, never inside this plugin.

Helps with GDPR, UK GDPR, CCPA/CPRA, LGPD, POPIA, and PIPEDA compliance.

## Features

* One-click connect: enter an email on the CookiesRegTech page in the Wagtail admin — a free account is created and the banner goes live, no copy-pasting required
* Opt-in (GDPR-style) and opt-out (US-style) consent templates, with geo-targeting on paid plans
* Automatic blocking of known advertising and analytics trackers until consent
* Google Consent Mode v2 signals set before Google tags execute
* Cookie scanner that discovers and categorises the cookies the site sets, with the detected list shown right inside the Wagtail admin
* Native Wagtail admin experience: a top-level **CookiesRegTech** item in the sidebar (alongside Pages, Images, Reports and your other apps), rendered inside the normal admin layout
* Full dark mode support: follows the Wagtail admin's light / dark / system theme (Account > Appearance)
* Signed-in jumps from the Wagtail admin straight into the consent dashboard
* Consent log with export, as required for GDPR accountability
* Accessible by design: WCAG 2.2 AA contrast, keyboard support, 44px targets

## Requirements

* Python 3.9 or newer
* Django 4.2 or newer
* Wagtail 4.1 or newer 

## Installation

1. Install the package:

   ```
   pip install wagtail-cookiesregtech
   ```

2. Add the app and the middleware to `settings.py`:

   ```python
   INSTALLED_APPS = [
       # ...
       "wagtail_cookiesregtech",
   ]

   MIDDLEWARE = [
       # ...
       "wagtail_cookiesregtech.middleware.BannerInjectionMiddleware",
   ]
   ```

   If the site uses `django.middleware.gzip.GZipMiddleware`, list it **before** the CookiesRegTech middleware, so the page is compressed after the script is added. Already-compressed responses are skipped rather than modified.

3. Run the migration and collect the static files:

   ```
   python manage.py migrate wagtail_cookiesregtech
   python manage.py collectstatic
   ```

4. Restart the server, sign in to the Wagtail admin, and click **CookiesRegTech** in the sidebar.
5. Enter an account email, accept the terms, and click **Connect website**.
6. New email: a free account is created instantly and the banner is live. Existing account: click the confirmation link that arrives by email, then press **Check status**.
7. Use **Open dashboard** on the CookiesRegTech page to customise the banner, run cookie scans, and view the consent log.

### Upgrading

```
pip install --upgrade wagtail-cookiesregtech
python manage.py migrate wagtail_cookiesregtech
python manage.py collectstatic
```

Then restart the server and hard-refresh the browser once (Ctrl+Shift+R) so the updated stylesheet loads. No settings changes are needed.

## After connecting

The CookiesRegTech page shows the account, plan, banner status, and the cookies found by the last scan, plus a banner on/off toggle, signed-in **Open dashboard** / **Upgrade plan** links (these open the external CookiesRegTech site in a new tab), and **Disconnect**.

Access follows Wagtail's own permission: any user who can access the Wagtail admin can see the page.

## Frequently Asked Questions

### Is a CookiesRegTech account required?

Yes — a free account, created directly from the CookiesRegTech page in the Wagtail admin. The banner configuration, cookie scanning, and consent log live in the dashboard at www.cookiesregtech.com.

### Does the plugin slow the site down?

No. It adds a single ~1KB loader script that never blocks page rendering; the banner itself loads asynchronously.

### The analytics code is pasted directly into the base template's head — is it still blocked?

The middleware injects the consent script immediately after the opening `<head>` tag of every rendered HTML page, so it runs before any analytics or tag manager code placed inside the head. Non-HTML responses, streaming responses, compressed responses, static and media files, and the Wagtail and Django admins (including page previews in the editor) are skipped. Google tags are additionally governed by Consent Mode either way.

### The Wagtail admin is not at `/admin/`. Does that matter?

No. The middleware looks up the real admin URL, so a custom mount point such as `/cms/` is skipped correctly.

### Where are the banner text, colors, or languages changed?

In the CookiesRegTech dashboard — changes publish to the site instantly, no plugin update needed.

### Does it work with the Wagtail dark theme?

Yes. The page uses Wagtail's own theme colours, so it switches with the admin's light, dark, or system setting.

### What data does the plugin send?

On connect: the account email and the site hostname, to create/link the account. Afterwards the CookiesRegTech page reads the connection status and detected cookie list from the CookiesRegTech API. Visitor consent choices are recorded by the banner script per the CookiesRegTech privacy policy (https://www.cookiesregtech.com/privacy-policy).

### What happens if I disconnect?

The banner turns off and the stored connection is removed from the site. The CookiesRegTech account and its data are unchanged, and you can reconnect at any time.
