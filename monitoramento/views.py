from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Count, Avg, F
from datetime import date
import json as _json
from .models import Demanda, TipoDemanda, StatusDemanda
from .forms import DemandaForm


class DemandaListView(LoginRequiredMixin, ListView):
    """
    Lista de demandas do monitoramento, com filtros por tipo, status e busca.
    Pode ser usada de duas formas:
        1. Sem `tipo_fixo`: lista todas as demandas (visão consolidada).
        2. Com `tipo_fixo`: lista apenas um tipo específico (visão por categoria).
    """

    model           = Demanda
    template_name   = "monitoramento/lista.html"
    context_object_name = "demandas"
    paginate_by     = 50

    # Subclasses definem este atributo para fixar o tipo exibido
    tipo_fixo: str | None = None

    def get_queryset(self):
        qs = Demanda.objects.all()

        if self.tipo_fixo:
            qs = qs.filter(tipo=self.tipo_fixo)

        # Filtro dinâmico por tipo (só na visão "todas")
        tipo_param = self.request.GET.get("tipo", "")
        if tipo_param and not self.tipo_fixo:
            qs = qs.filter(tipo=tipo_param)

        # Filtro por status
        status_param = self.request.GET.get("status", "")
        if status_param:
            qs = qs.filter(status=status_param)
        else:
            # Fora da aba Concluídas, nunca mostra concluídas (elas ficam na aba própria)
            qs = qs.exclude(status=StatusDemanda.CONCLUIDA)

        # Busca textual
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(processo_sei__icontains=q)
                | Q(observacoes__icontains=q)
                | Q(localizacao__icontains=q)
            )

        return qs.order_by("priorizacao", "-data_inicio")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tipo_fixo"]      = self.tipo_fixo
        ctx["tipo_display"]   = dict(TipoDemanda.choices).get(self.tipo_fixo, "Todas") if self.tipo_fixo else "Todas"
        ctx["tipos"]          = TipoDemanda.choices
        ctx["statuses"]       = StatusDemanda.choices
        ctx["q"]              = self.request.GET.get("q", "")
        ctx["filtro_tipo"]    = self.request.GET.get("tipo", "")
        ctx["filtro_status"]  = self.request.GET.get("status", "")
        ctx["total"]          = self.get_queryset().count()

        # Contadores por tipo para o resumo rápido (excluindo concluídas dessas abas)
        ctx["contadores"] = {
            tipo: Demanda.objects.filter(tipo=tipo).exclude(status=StatusDemanda.CONCLUIDA).count()
            for tipo, _ in TipoDemanda.choices
        }
        ctx["contadores"]["concluidas"] = Demanda.objects.filter(status=StatusDemanda.CONCLUIDA).count()
        return ctx


# Visões fixas por tipo ---------------------------------------------------

class EvolutivaListView(DemandaListView):
    tipo_fixo = TipoDemanda.EVOLUTIVA


class CorretivaListView(DemandaListView):
    tipo_fixo = TipoDemanda.CORRETIVA


class IndicacaoRubricaListView(DemandaListView):
    tipo_fixo = TipoDemanda.INDICACAO_RUBRICA


class CriacaoObjetoListView(DemandaListView):
    tipo_fixo = TipoDemanda.CRIACAO_OBJETO


class ConcluídasListView(DemandaListView):
    """
    Lista todas as demandas com status=concluida, independente do tipo.
    Quando uma demanda de qualquer aba é marcada como Concluída, aparece aqui.
    Quando o status é alterado de volta, retorna à aba de origem.
    """
    template_name = "monitoramento/lista.html"

    def get_queryset(self):
        qs = Demanda.objects.filter(status=StatusDemanda.CONCLUIDA)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(processo_sei__icontains=q)
                | Q(observacoes__icontains=q)
                | Q(localizacao__icontains=q)
            )
        tipo_param = self.request.GET.get("tipo", "")
        if tipo_param:
            qs = qs.filter(tipo=tipo_param)
        return qs.order_by("-data_conclusao", "nome")

    def get_context_data(self, **kwargs):
        ctx = super(DemandaListView, self).get_context_data(**kwargs)
        ctx["tipo_fixo"]     = None
        ctx["tipo_display"]  = "Concluídas"
        ctx["is_concluidas"] = True
        ctx["tipos"]         = TipoDemanda.choices
        ctx["statuses"]      = StatusDemanda.choices
        ctx["q"]             = self.request.GET.get("q", "")
        ctx["filtro_tipo"]   = self.request.GET.get("tipo", "")
        ctx["filtro_status"] = ""
        ctx["total"]         = self.get_queryset().count()
        ctx["paginate_by"]   = self.paginate_by
        ctx["contadores"] = {
            tipo: Demanda.objects.filter(tipo=tipo).exclude(status=StatusDemanda.CONCLUIDA).count()
            for tipo, _ in TipoDemanda.choices
        }
        ctx["contadores"]["concluidas"] = Demanda.objects.filter(status=StatusDemanda.CONCLUIDA).count()
        # Paginação manual
        from django.core.paginator import Paginator
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get("page", 1)
        ctx["page_obj"]       = paginator.get_page(page)
        ctx["demandas"]       = ctx["page_obj"].object_list
        ctx["is_paginated"]   = paginator.num_pages > 1
        return ctx


# Dashboard --------------------------------------------------------------

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        hoje = date.today()

        ativas = Demanda.objects.exclude(status=StatusDemanda.CONCLUIDA)
        concluidas = Demanda.objects.filter(status=StatusDemanda.CONCLUIDA)
        todas = Demanda.objects.all()

        # ── KPIs ──────────────────────────────────────────────────────────
        total_ativas    = ativas.count()
        total_concluidas = concluidas.count()
        total_geral     = todas.count()
        total_andamento = ativas.filter(status=StatusDemanda.EM_ANDAMENTO).count()
        total_nao_inic  = ativas.filter(status=StatusDemanda.NAO_INICIADA).count()
        total_reiteradas = ativas.filter(reiterada=True).count()
        taxa_conclusao  = round(total_concluidas / total_geral * 100) if total_geral else 0

        # Média de dias em espera (em andamento com data_inicio)
        dias_list = [
            (hoje - d.data_inicio).days
            for d in ativas.filter(status=StatusDemanda.EM_ANDAMENTO, data_inicio__isnull=False)
        ]
        media_dias = round(sum(dias_list) / len(dias_list)) if dias_list else 0
        em_atraso  = sum(1 for d in dias_list if d > 365)

        # ── Gráfico 1: Ativas por tipo (donut) ──────────────────────────
        por_tipo = {
            tipo: ativas.filter(tipo=tipo).count()
            for tipo, _ in TipoDemanda.choices
        }

        # ── Gráfico 2: Status por tipo (stacked bar) ────────────────────
        status_por_tipo = []
        for tipo, label in TipoDemanda.choices:
            qs = Demanda.objects.filter(tipo=tipo)
            status_por_tipo.append({
                "tipo": label,
                "nao_iniciada": qs.filter(status=StatusDemanda.NAO_INICIADA).count(),
                "em_andamento": qs.filter(status=StatusDemanda.EM_ANDAMENTO).count(),
                "concluida":    qs.filter(status=StatusDemanda.CONCLUIDA).count(),
            })

        # ── Gráfico 3: Concluídas por mês (bar) ─────────────────────────
        from collections import defaultdict
        conc_por_mes = defaultdict(int)
        for d in concluidas.filter(data_conclusao__isnull=False).values("data_conclusao"):
            chave = d["data_conclusao"].strftime("%Y-%m")
            conc_por_mes[chave] += 1
        meses_ordenados = sorted(conc_por_mes.keys())
        conc_labels = [m for m in meses_ordenados]
        conc_values = [conc_por_mes[m] for m in meses_ordenados]
        # Formata labels como "Jan/24"
        from datetime import datetime as _dt
        meses_pt = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        conc_labels_fmt = []
        for m in meses_ordenados:
            y, mo = m.split("-")
            conc_labels_fmt.append(f"{meses_pt[int(mo)-1]}/{y[2:]}")

        # ── Gráfico 4: Faixas de dias em espera (ativas em andamento) ────
        faixas = {"≤30d": 0, "31–90d": 0, "91–180d": 0, "181–365d": 0, ">365d": 0}
        for d in dias_list:
            if d <= 30:   faixas["≤30d"] += 1
            elif d <= 90:  faixas["31–90d"] += 1
            elif d <= 180: faixas["91–180d"] += 1
            elif d <= 365: faixas["181–365d"] += 1
            else:          faixas[">365d"] += 1

        # ── Gráfico 5: Top 5 mais antigas em andamento ───────────────────
        top_antigas = []
        for d in ativas.filter(status=StatusDemanda.EM_ANDAMENTO, data_inicio__isnull=False).order_by("data_inicio")[:5]:
            top_antigas.append({
                "nome":  d.nome[:50] + ("…" if len(d.nome) > 50 else ""),
                "dias":  (hoje - d.data_inicio).days,
                "tipo":  d.get_tipo_display(),
            })

        ctx = {
            # KPIs
            "total_ativas":      total_ativas,
            "total_concluidas":  total_concluidas,
            "total_geral":       total_geral,
            "total_andamento":   total_andamento,
            "total_nao_inic":    total_nao_inic,
            "total_reiteradas":  total_reiteradas,
            "taxa_conclusao":    taxa_conclusao,
            "media_dias":        media_dias,
            "em_atraso":         em_atraso,
            # Contadores por tipo (excluindo concluídas) para mini-KPIs
            "contadores_tipo": {
                tipo: ativas.filter(tipo=tipo).count()
                for tipo, _ in TipoDemanda.choices
            },
            # Dados para gráficos (JSON)
            "chart_por_tipo_labels": _json.dumps([label for _, label in TipoDemanda.choices]),
            "chart_por_tipo_data":   _json.dumps([por_tipo[t] for t, _ in TipoDemanda.choices]),
            "chart_status_data":     _json.dumps(status_por_tipo),
            "chart_conc_labels":     _json.dumps(conc_labels_fmt),
            "chart_conc_data":       _json.dumps(conc_values),
            "chart_faixas_labels":   _json.dumps(list(faixas.keys())),
            "chart_faixas_data":     _json.dumps(list(faixas.values())),
            "top_antigas":           top_antigas,
        }
        return render(request, "monitoramento/dashboard.html", ctx)


# CRUD -------------------------------------------------------------------

class DemandaCreateView(LoginRequiredMixin, CreateView):
    model         = Demanda
    form_class    = DemandaForm
    template_name = "monitoramento/form.html"

    def get_success_url(self):
        messages.success(self.request, "Demanda criada com sucesso.")
        return reverse_lazy("monitoramento:lista")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Demanda"
        ctx["cancelar_url"] = reverse_lazy("monitoramento:lista")
        return ctx


class DemandaUpdateView(LoginRequiredMixin, UpdateView):
    model         = Demanda
    form_class    = DemandaForm
    template_name = "monitoramento/form.html"

    def get_success_url(self):
        messages.success(self.request, "Demanda atualizada com sucesso.")
        return reverse_lazy("monitoramento:lista")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar — {self.object.nome[:60]}"
        ctx["cancelar_url"] = reverse_lazy("monitoramento:lista")
        ctx["object"] = self.object
        return ctx


class DemandaDeleteView(LoginRequiredMixin, DeleteView):
    model         = Demanda
    template_name = "monitoramento/confirmar_exclusao.html"

    def get_success_url(self):
        messages.success(self.request, "Demanda excluída.")
        return reverse_lazy("monitoramento:lista")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancelar_url"] = reverse_lazy("monitoramento:lista")
        return ctx


class ReordenarPrioridadeView(LoginRequiredMixin, View):
    """
    GET  → página com lista drag-and-drop de todas as demandas com priorização.
    POST → recebe JSON {"ordem": [pk1, pk2, ...]} e reatribui prioridades 1, 2, 3…
    """

    def get(self, request):
        from django.shortcuts import render
        colunas = []
        for tipo, label in TipoDemanda.choices:
            items = list(Demanda.objects.filter(tipo=tipo).order_by("priorizacao", "nome"))
            prio_ativa = any(d.priorizacao is not None for d in items)
            colunas.append({
                "tipo": tipo,
                "label": label,
                "items": items,
                "prio_ativa": prio_ativa,
            })
        return render(request, "monitoramento/reordenar.html", {"colunas": colunas})

    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
            # data = {"evolutiva": [pk1, pk2, ...], "corretiva": [...], ...}
            with transaction.atomic():
                for tipo, pks in data.items():
                    for i, pk in enumerate(pks, start=1):
                        Demanda.objects.filter(pk=pk, tipo=tipo).update(priorizacao=i)
                    pks_set = {int(pk) for pk in pks}
                    Demanda.objects.filter(tipo=tipo).exclude(pk__in=pks_set).update(priorizacao=None)
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "erro": str(e)}, status=400)
