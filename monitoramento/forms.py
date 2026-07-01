from django import forms
from .models import Demanda, TipoDemanda, StatusDemanda


class DemandaForm(forms.ModelForm):
    class Meta:
        model  = Demanda
        fields = [
            "nome",
            "tipo",
            "classificacao",
            "status",
            "data_inicio",
            "data_conclusao",
            "processo_sei",
            "processo_relacionado",
            "alm",
            "localizacao",
            "reiterada",
            "data_reiteracao",
            "priorizacao",
            "observacoes",
        ]
        widgets = {
            "nome": forms.Textarea(attrs={"rows": 3}),
            "processo_relacionado": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 4}),
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_conclusao": forms.DateInput(attrs={"type": "date"}),
            "data_reiteracao": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        data_conclusao = cleaned.get("data_conclusao")
        reiterada = cleaned.get("reiterada")
        data_reiteracao = cleaned.get("data_reiteracao")

        # Garante consistência mínima para demandas finalizadas.
        if status == StatusDemanda.CONCLUIDA and not data_conclusao:
            self.add_error("data_conclusao", "Informe a data de conclusão quando o status for Concluída.")

        if reiterada and not data_reiteracao:
            self.add_error("data_reiteracao", "Informe a data de reiteração.")
        return cleaned
