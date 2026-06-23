from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("design-system/", views.DesignSystemView.as_view(), name="design_system"),
]
