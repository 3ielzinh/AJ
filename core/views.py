from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "core/home.html"


class DesignSystemView(TemplateView):
    template_name = "core/design_system.html"

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
