from django.contrib import admin
from .models import Demanda, TipoDemanda


@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display  = ("nome", "tipo", "status", "data_inicio", "data_conclusao", "dias_espera_display", "reiterada")
    list_filter   = ("tipo", "status", "reiterada")
    search_fields = ("nome", "processo_sei", "observacoes")
    date_hierarchy = "data_inicio"
    readonly_fields = ("criado_em", "atualizado_em", "dias_espera_display")

    @admin.display(description="Dias")
    def dias_espera_display(self, obj):
        return obj.dias_espera_display
