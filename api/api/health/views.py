"""Health check view — demo-safe version"""

import os
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views import View

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


class HealthCheckView(View):
    http_method_names = ["get", "head"]

    def get(self, request, *args, **kwargs):
        payload = {
            "status": "healthy",
            "version": APP_VERSION,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "platform": "Glapagos — AI Corridor of the Americas",
            "services": {
                "api": {"status": "ok"},
            },
        }
        return JsonResponse(payload, status=200)
