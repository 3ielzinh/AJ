from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"


class DesignSystemView(LoginRequiredMixin, TemplateView):
    template_name = "core/design_system.html"

    def dispatch(self, request, *args, **kwargs):
        # Oculta a existencia da rota para usuarios sem permissao.
        if not request.user.is_staff:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["icons"] = [
            "solar:layers-minimalistic-linear",
            "solar:graph-up-linear",
            "solar:shield-check-linear",
            "solar:atom-linear",
            "solar:widget-linear",
            "solar:stars-linear",
            "solar:document-linear",
            "solar:calendar-linear",
            "solar:user-linear",
            "solar:settings-linear",
            "solar:search-linear",
            "solar:bell-linear",
        ]
        return ctx
