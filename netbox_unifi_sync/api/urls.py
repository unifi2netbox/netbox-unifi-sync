# NOTE: This module is not currently wired into the plugin URL routing (urls.py).
# The views exist but are only reachable if this is included via NetBox API router.
# Needs review before enabling: ensure NetBox REST API plugin registration is in place.
from __future__ import annotations

from django.urls import path

from netbox_unifi_sync import views

app_name = "netbox_unifi_sync-api"

urlpatterns = (
    path("status/", views.api_status_view, name="status"),
    path("controllers/<int:pk>/test/", views.controller_test_api_view, name="controller-test"),
)
