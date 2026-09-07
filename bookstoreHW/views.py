from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.shortcuts import render, redirect


def error_404(request, exception):
    return render(request, "error_404.html", status=404)


def error_403(request, exception):
    return render(request, "error_403.html", status=403)


def index(request):
    return redirect("/shop/")

def health_check(request):

    checks = {"database": "ok", "cache": "ok"}
    is_healthy = True

    try:
        connections["default"].cursor()
    except OperationalError:
        checks["database"] = "error"
        is_healthy = False

    try:
        cache.set("health_check_probe", "ok", timeout=5)
        if cache.get("health_check_probe") != "ok":
            raise ValueError("cache readback mismatch")
    except Exception:
        checks["cache"] = "error"
        is_healthy = False

    payload = {"status": "healthy" if is_healthy else "unhealthy", "checks": checks}
    return JsonResponse(payload, status=200 if is_healthy else 503)