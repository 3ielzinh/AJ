"""URLs raiz do projeto AJ."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def healthcheck(_request):
    """Endpoint de monitoramento. Retorna 200 se o banco responde."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"status": "error", "detail": str(exc)}, status=503)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="health"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls", namespace="core")),
    path("monitoramento/", include("monitoramento.urls", namespace="monitoramento")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
