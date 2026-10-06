from django.urls import path

from . import views

app_name = "wagtail_cookiesregtech"

urlpatterns = [
    path("", views.settings_page, name="settings"),
]
