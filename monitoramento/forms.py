from django import forms
from .models import Demanda, ObjetoGestao, TipoDemanda, StatusDemanda


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


class ObjetoGestaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css_class = "form-select"
            elif isinstance(widget, forms.Textarea):
                css_class = "form-textarea"
            else:
                css_class = "form-input"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css_class}".strip()

    class Meta:
        model = ObjetoGestao
        fields = [
            "id_objeto",
            "nome",
            "descricao",
            "grupo",
            "ativo",
            "data_encerramento",
            "processo_sei",
            "ajs_ativas",
            "tipo_objeto",
            "carater",
            "fluxo_confirmacao",
            "passivel_absorcao",
            "tema",
            "subtema",
            "pedido_inicial",
            "limite_maximo_objeto",
            "observacao",
        ]
        widgets = {
            "data_encerramento": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "ajs_ativas": forms.Textarea(attrs={"rows": 3}),
            "pedido_inicial": forms.Textarea(attrs={"rows": 3}),
            "observacao": forms.Textarea(attrs={"rows": 4}),
        }
