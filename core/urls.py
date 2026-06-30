from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("perfil/", views.ProfileView.as_view(), name="perfil"),
    path("perfil/exportar-csv/", views.export_profile_documents_csv, name="perfil_exportar_csv"),
    path("accounts/signup/", views.signup_view, name="signup"),
    path("design-system/", views.DesignSystemView.as_view(), name="design_system"),
]
