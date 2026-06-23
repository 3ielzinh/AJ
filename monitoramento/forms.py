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
        reiterada = cleaned.get("reiterada")
        data_reiteracao = cleaned.get("data_reiteracao")
        if reiterada and not data_reiteracao:
            self.add_error("data_reiteracao", "Informe a data de reiteração.")
        return cleaned
