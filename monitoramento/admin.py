from django.contrib import admin
from .models import Demanda, ProcessoSEI, DocumentoSEI, TipoDemanda


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


@admin.register(ProcessoSEI)
class ProcessoSEIAdmin(admin.ModelAdmin):
    list_display = ("numero_processo", "primeira_data_assinatura", "unidade_principal", "total_documentos", "atualizado_em")
    search_fields = ("numero_processo", "assunto_principal", "unidade_principal")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(DocumentoSEI)
class DocumentoSEIAdmin(admin.ModelAdmin):
    list_display = ("numero_documento", "processo", "tipo", "data_assinatura", "unidade", "atualizado_em")
    list_filter = ("tipo", "unidade")
    search_fields = (
        "numero_documento",
        "processo__numero_processo",
        "assunto",
        "resumo",
        "assinantes",
    )
    readonly_fields = ("criado_em", "atualizado_em")
