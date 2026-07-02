from django.views.generic import ListView, View, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Count, Avg, F
from datetime import date, datetime
import json as _json
import unicodedata
from .models import Demanda, DocumentoSEI, ObjetoGestao, ProcessoSEI, TipoDemanda, StatusDemanda
from .forms import DemandaForm, ObjetoGestaoForm


GESTAO_OBJETOS_OBS_PREFIX = "Importacao Gestao de Objetos (planilha):"

GESTAO_OBJETOS_OBS_FIELDS = {
    "ID DO OBJETO",
    "DESCRICAO",
    "ATIVO",
    "DATA ENCERRAMENTO",
    "AJS ATIVAS",
    "TIPO DE OBJETO",
    "CARATER",
    "FLUXO DE CONFIRMACAO",
    "PASSIVEL DE ABSORCAO",
    "TEMA",
    "SUBTEMA",
    "PEDIDO INICIAL",
    "LIMITE MAXIMO DO OBJETO",
    "OBSERVACAO ORIGINAL",
    "ABA ORIGEM",
    "LINHA ORIGEM",
}


def _normalizar_texto(valor: str | None) -> str:
    if not valor:
        return ""
    txt = unicodedata.normalize("NFKD", str(valor).strip())
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return " ".join(txt.upper().split())


def _extrair_campos_gestao_objetos(observacoes: str | None) -> dict[str, str]:
    """
    Extrai campos estruturados apenas quando o texto segue o padrao da importacao.
    Nao tenta inferir formato livre para evitar parser fragil.
    """
    if not observacoes:
        return {}

    texto = observacoes.strip()
    if not texto.startswith(GESTAO_OBJETOS_OBS_PREFIX):
        return {}

    campos: dict[str, str] = {}
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha.startswith("- ") or ":" not in linha:
            continue
        chave, valor = linha[2:].split(":", 1)
        chave_norm = _normalizar_texto(chave)
        if chave_norm not in GESTAO_OBJETOS_OBS_FIELDS:
            continue
        campos[chave_norm] = valor.strip()
    return campos


class MonitoramentoHubView(LoginRequiredMixin, TemplateView):
    template_name = "monitoramento/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "total_processos_sei": ProcessoSEI.objects.count(),
                "total_documentos_sei": DocumentoSEI.objects.count(),
                "total_demandas": Demanda.objects.count(),
                "total_concluidas": Demanda.objects.filter(status=StatusDemanda.CONCLUIDA).count(),
            }
        )
        return ctx


class MonitoramentoSEIView(LoginRequiredMixin, ListView):
    model = ProcessoSEI
    template_name = "monitoramento/sei_lista.html"
    context_object_name = "processos"
    paginate_by = 25

    def get_queryset(self):
        qs = ProcessoSEI.objects.all().prefetch_related("documentos")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(numero_processo__icontains=q)
                | Q(assunto_principal__icontains=q)
                | Q(unidade_principal__icontains=q)
                | Q(documentos__numero_documento__icontains=q)
                | Q(documentos__assunto__icontains=q)
                | Q(documentos__tipo__icontains=q)
                | Q(documentos__unidade__icontains=q)
                | Q(documentos__resumo__icontains=q)
                | Q(documentos__assinantes__icontains=q)
                | Q(documentos__criado_por__icontains=q)
                | Q(documentos__versao_por__icontains=q)
                | Q(documentos__arquivo_nome__icontains=q)
            ).distinct()
        return qs.order_by("-total_documentos", "numero_processo")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["total_processos"] = ProcessoSEI.objects.count()
        ctx["total_documentos"] = DocumentoSEI.objects.count()
        return ctx


class MonitoramentoAJView(LoginRequiredMixin, TemplateView):
    template_name = "monitoramento/submonitoramento.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Monitoramento AJ"
        ctx["descricao"] = "Este monitoramento estara separado do Monitoramento Sistemico."
        return ctx


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

    def aplicar_busca_global(self, qs, termo: str):
        """
        Aplica busca ampla sobre campos textuais, enumerações, datas e números.
        """
        termo = termo.strip()
        if not termo:
            return qs

        q_obj = (
            Q(nome__icontains=termo)
            | Q(tipo__icontains=termo)
            | Q(classificacao__icontains=termo)
            | Q(status__icontains=termo)
            | Q(processo_sei__icontains=termo)
            | Q(processo_relacionado__icontains=termo)
            | Q(alm__icontains=termo)
            | Q(localizacao__icontains=termo)
            | Q(observacoes__icontains=termo)
        )

        termo_lower = termo.lower()

        # Permite buscar por labels legíveis de tipo.
        tipo_labels = {
            "evolutiva": TipoDemanda.EVOLUTIVA,
            "corretiva": TipoDemanda.CORRETIVA,
            "gestao de objetos": TipoDemanda.GESTAO_OBJETOS,
            "gestão de objetos": TipoDemanda.GESTAO_OBJETOS,
            # Compatibilidade com nomenclatura antiga.
            "indicacao de rubrica": TipoDemanda.GESTAO_OBJETOS,
            "indicação de rubrica": TipoDemanda.GESTAO_OBJETOS,
            "criacao de objeto": TipoDemanda.GESTAO_OBJETOS,
            "criação de objeto": TipoDemanda.GESTAO_OBJETOS,
        }
        if termo_lower in tipo_labels:
            q_obj |= Q(tipo=tipo_labels[termo_lower])

        # Permite buscar por labels legíveis de status.
        status_labels = {
            "nao iniciada": StatusDemanda.NAO_INICIADA,
            "não iniciada": StatusDemanda.NAO_INICIADA,
            "em andamento": StatusDemanda.EM_ANDAMENTO,
            "concluida": StatusDemanda.CONCLUIDA,
            "concluída": StatusDemanda.CONCLUIDA,
        }
        if termo_lower in status_labels:
            q_obj |= Q(status=status_labels[termo_lower])

        # Busca numérica em priorização.
        if termo.isdigit():
            q_obj |= Q(priorizacao=int(termo))

        # Busca por reiteração com termos comuns.
        if termo_lower in {"sim", "true", "verdadeiro", "reiterada", "reiterado"}:
            q_obj |= Q(reiterada=True)
        if termo_lower in {"nao", "não", "false", "falso"}:
            q_obj |= Q(reiterada=False)

        # Busca por datas em formatos usuais.
        formatos_data = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        for formato in formatos_data:
            try:
                data_digitada = datetime.strptime(termo, formato).date()
                q_obj |= (
                    Q(data_inicio=data_digitada)
                    | Q(data_conclusao=data_digitada)
                    | Q(data_reiteracao=data_digitada)
                )
                break
            except ValueError:
                continue

        return qs.filter(q_obj)

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
        q = self.request.GET.get("q", "").strip()
        if status_param:
            qs = qs.filter(status=status_param)
        else:
            # Fora da aba Concluídas, nunca mostra concluídas (elas ficam na aba própria)
            # Exceção: com busca preenchida, inclui também concluídas para busca global.
            if not q:
                qs = qs.exclude(status=StatusDemanda.CONCLUIDA)

        # Busca textual
        if q:
            qs = self.aplicar_busca_global(qs, q)

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


class GestaoObjetosListView(LoginRequiredMixin, ListView):
    model = ObjetoGestao
    template_name = "monitoramento/gestao_objetos.html"
    context_object_name = "objetos"
    paginate_by = 40

    @staticmethod
    def _fluxo_categoria(valor: str | None) -> str:
        normalizado = _normalizar_texto(valor)
        if not normalizado:
            return ""
        if "DESCENTRALIZADO" in normalizado:
            return "descentralizado"
        if "CENTRALIZADO" in normalizado:
            return "centralizado"
        return ""

    def get_queryset(self):
        qs = ObjetoGestao.objects.all().order_by("grupo", "nome")

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(descricao__icontains=q)
                | Q(grupo__icontains=q)
                | Q(processo_sei__icontains=q)
                | Q(tema__icontains=q)
                | Q(subtema__icontains=q)
                | Q(pedido_inicial__icontains=q)
                | Q(observacao__icontains=q)
            )

        grupo_param = self.request.GET.get("grupo", "").strip()
        if grupo_param:
            qs = qs.filter(grupo=grupo_param)

        ativo_param = self.request.GET.get("ativo", "").strip().lower()
        if ativo_param == "sim":
            qs = qs.filter(ativo=True)
        elif ativo_param == "nao":
            qs = qs.filter(ativo=False)
        elif ativo_param == "sem":
            qs = qs.filter(ativo__isnull=True)

        carater_param = self.request.GET.get("carater", "").strip()
        if carater_param:
            qs = qs.filter(carater=carater_param)

        fluxo_param = self.request.GET.get("fluxo", "").strip()
        if fluxo_param:
            qs = qs.filter(fluxo_confirmacao=fluxo_param)

        tema_param = self.request.GET.get("tema", "").strip()
        if tema_param:
            qs = qs.filter(tema=tema_param)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        filtros = {
            "q": self.request.GET.get("q", "").strip(),
            "grupo": self.request.GET.get("grupo", "").strip(),
            "ativo": self.request.GET.get("ativo", "").strip().lower(),
            "carater": self.request.GET.get("carater", "").strip(),
            "fluxo": self.request.GET.get("fluxo", "").strip(),
            "tema": self.request.GET.get("tema", "").strip(),
        }

        base_qs = ObjetoGestao.objects.all()
        objetos_base = list(base_qs.only("ativo", "carater", "fluxo_confirmacao", "grupo", "tema"))

        total_objetos = len(objetos_base)
        ativos = sum(1 for obj in objetos_base if obj.ativo is True)
        inativos = sum(1 for obj in objetos_base if obj.ativo is False)
        sem_ativo = sum(1 for obj in objetos_base if obj.ativo is None)
        financeiros = sum(1 for obj in objetos_base if "FINANCEIRO" in _normalizar_texto(obj.carater))
        cadastrais = sum(1 for obj in objetos_base if "CADASTRAL" in _normalizar_texto(obj.carater))
        fluxo_centralizado = sum(
            1 for obj in objetos_base if self._fluxo_categoria(obj.fluxo_confirmacao) == "centralizado"
        )
        fluxo_descentralizado = sum(
            1 for obj in objetos_base if self._fluxo_categoria(obj.fluxo_confirmacao) == "descentralizado"
        )

        filtros_ativos_labels = [label for label, value in filtros.items() if value]

        ctx.update(
            {
                "tipo_fixo": TipoDemanda.GESTAO_OBJETOS,
                "tipo_display": "Gestao de Objetos",
                "q": filtros["q"],
                "filtro_grupo": filtros["grupo"],
                "filtro_ativo": filtros["ativo"],
                "filtro_carater": filtros["carater"],
                "filtro_fluxo": filtros["fluxo"],
                "filtro_tema": filtros["tema"],
                "total": self.get_queryset().count(),
                "total_catalogo": total_objetos,
                "kpi_ativos": ativos,
                "kpi_inativos": inativos,
                "kpi_sem_ativo": sem_ativo,
                "kpi_financeiros": financeiros,
                "kpi_cadastrais": cadastrais,
                "kpi_fluxo_centralizado": fluxo_centralizado,
                "kpi_fluxo_descentralizado": fluxo_descentralizado,
                "grupos_disponiveis": sorted(base_qs.exclude(grupo="").values_list("grupo", flat=True).distinct()),
                "carateres_disponiveis": sorted(base_qs.exclude(carater="").values_list("carater", flat=True).distinct()),
                "fluxos_disponiveis": sorted(
                    base_qs.exclude(fluxo_confirmacao="").values_list("fluxo_confirmacao", flat=True).distinct()
                ),
                "temas_disponiveis": sorted(base_qs.exclude(tema="").values_list("tema", flat=True).distinct()),
                "filtros_ativos": filtros_ativos_labels,
                "contadores": {
                    TipoDemanda.EVOLUTIVA: Demanda.objects.filter(tipo=TipoDemanda.EVOLUTIVA)
                    .exclude(status=StatusDemanda.CONCLUIDA)
                    .count(),
                    TipoDemanda.CORRETIVA: Demanda.objects.filter(tipo=TipoDemanda.CORRETIVA)
                    .exclude(status=StatusDemanda.CONCLUIDA)
                    .count(),
                    TipoDemanda.GESTAO_OBJETOS: total_objetos,
                    "concluidas": Demanda.objects.filter(status=StatusDemanda.CONCLUIDA).count(),
                },
            }
        )
        return ctx


class IndicacaoRubricaListView(GestaoObjetosListView):
    pass


class CriacaoObjetoListView(GestaoObjetosListView):
    pass


class ObjetoGestaoCreateView(LoginRequiredMixin, CreateView):
    model = ObjetoGestao
    form_class = ObjetoGestaoForm
    template_name = "monitoramento/gestao_objeto_form.html"
    success_url = reverse_lazy("monitoramento:gestao_objetos")

    def form_valid(self, form):
        messages.success(self.request, "Objeto cadastrado com sucesso.")
        return super().form_valid(form)


class ObjetoGestaoUpdateView(LoginRequiredMixin, UpdateView):
    model = ObjetoGestao
    form_class = ObjetoGestaoForm
    template_name = "monitoramento/gestao_objeto_form.html"
    success_url = reverse_lazy("monitoramento:gestao_objetos")

    def form_valid(self, form):
        messages.success(self.request, "Objeto atualizado com sucesso.")
        return super().form_valid(form)


class ObjetoGestaoDeleteView(LoginRequiredMixin, DeleteView):
    model = ObjetoGestao
    template_name = "monitoramento/gestao_objeto_confirmar_exclusao.html"
    success_url = reverse_lazy("monitoramento:gestao_objetos")

    def form_valid(self, form):
        messages.success(self.request, "Objeto removido com sucesso.")
        return super().form_valid(form)


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
            qs = self.aplicar_busca_global(qs, q)
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
    @staticmethod
    def _aplicar_busca_dashboard(qs, termo: str):
        termo = termo.strip()
        if not termo:
            return qs

        q_obj = (
            Q(nome__icontains=termo)
            | Q(tipo__icontains=termo)
            | Q(classificacao__icontains=termo)
            | Q(status__icontains=termo)
            | Q(processo_sei__icontains=termo)
            | Q(processo_relacionado__icontains=termo)
            | Q(alm__icontains=termo)
            | Q(localizacao__icontains=termo)
            | Q(observacoes__icontains=termo)
        )

        termo_lower = termo.lower()
        tipo_labels = {
            "evolutiva": TipoDemanda.EVOLUTIVA,
            "corretiva": TipoDemanda.CORRETIVA,
            "gestao de objetos": TipoDemanda.GESTAO_OBJETOS,
            "gestão de objetos": TipoDemanda.GESTAO_OBJETOS,
        }
        if termo_lower in tipo_labels:
            q_obj |= Q(tipo=tipo_labels[termo_lower])

        status_labels = {
            "nao iniciada": StatusDemanda.NAO_INICIADA,
            "não iniciada": StatusDemanda.NAO_INICIADA,
            "em andamento": StatusDemanda.EM_ANDAMENTO,
            "concluida": StatusDemanda.CONCLUIDA,
            "concluída": StatusDemanda.CONCLUIDA,
        }
        if termo_lower in status_labels:
            q_obj |= Q(status=status_labels[termo_lower])

        if termo.isdigit():
            q_obj |= Q(priorizacao=int(termo))

        for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                data_digitada = datetime.strptime(termo, formato).date()
                q_obj |= (
                    Q(data_inicio=data_digitada)
                    | Q(data_conclusao=data_digitada)
                    | Q(data_reiteracao=data_digitada)
                )
                break
            except ValueError:
                continue

        return qs.filter(q_obj)

    def get(self, request):
        hoje = date.today()

        q = request.GET.get("q", "").strip()
        tipo_param = request.GET.get("tipo", "").strip()
        status_param = request.GET.get("status", "").strip()
        ano_param = request.GET.get("ano", "").strip()
        mes_param = request.GET.get("mes", "").strip()

        base_qs = Demanda.objects.all()

        if q:
            base_qs = self._aplicar_busca_dashboard(base_qs, q)

        if tipo_param:
            base_qs = base_qs.filter(tipo=tipo_param)

        if status_param:
            base_qs = base_qs.filter(status=status_param)

        if ano_param.isdigit():
            base_qs = base_qs.filter(models.Q(data_inicio__year=int(ano_param)) | models.Q(data_conclusao__year=int(ano_param)))

        if mes_param.isdigit():
            base_qs = base_qs.filter(models.Q(data_inicio__month=int(mes_param)) | models.Q(data_conclusao__month=int(mes_param)))

        ativas = base_qs.exclude(status=StatusDemanda.CONCLUIDA)
        concluidas = base_qs.filter(status=StatusDemanda.CONCLUIDA)
        todas = base_qs

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
            observacoes = (d.observacoes or "").strip().replace("\n", " ").replace("\r", " ")
            top_antigas.append({
                "id": d.id,
                "nome":  d.nome[:50] + ("…" if len(d.nome) > 50 else ""),
                "nome_completo": d.nome,
                "dias":  (hoje - d.data_inicio).days,
                "tipo":  d.get_tipo_display(),
                "status": d.get_status_display(),
                "status_code": d.status,
                "processo_sei": d.processo_sei or "—",
                "data_inicio": d.data_inicio,
                "data_conclusao": d.data_conclusao,
                "localizacao": d.localizacao or "—",
                "priorizacao": d.priorizacao,
                "reiterada": d.reiterada,
                "observacoes": observacoes,
            })

        max_dias = max((item["dias"] for item in top_antigas), default=1) or 1

        anos = sorted({
            ano
            for ano in (
                list(Demanda.objects.exclude(data_inicio__isnull=True).values_list("data_inicio__year", flat=True))
                + list(Demanda.objects.exclude(data_conclusao__isnull=True).values_list("data_conclusao__year", flat=True))
            )
            if ano
        }, reverse=True)
        meses = [
            ("1", "Janeiro"),
            ("2", "Fevereiro"),
            ("3", "Março"),
            ("4", "Abril"),
            ("5", "Maio"),
            ("6", "Junho"),
            ("7", "Julho"),
            ("8", "Agosto"),
            ("9", "Setembro"),
            ("10", "Outubro"),
            ("11", "Novembro"),
            ("12", "Dezembro"),
        ]

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
            "max_dias_top":          max_dias,
            "q":                     q,
            "filtro_tipo":           tipo_param,
            "filtro_status":         status_param,
            "filtro_ano":            ano_param,
            "filtro_mes":            mes_param,
            "anos_disponiveis":      anos,
            "meses_disponiveis":     meses,
            "filtros_ativos":        bool(q or tipo_param or status_param or ano_param or mes_param),
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

    def form_valid(self, form):
        demanda = form.save(commit=False)
        if demanda.status == StatusDemanda.CONCLUIDA:
            demanda.priorizacao = None
        demanda.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Demanda atualizada com sucesso.")
        if getattr(self.object, "status", None) == StatusDemanda.CONCLUIDA:
            return reverse_lazy("monitoramento:concluidas")
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
            items = list(
                Demanda.objects
                .filter(tipo=tipo)
                .exclude(status=StatusDemanda.CONCLUIDA)
                .order_by("priorizacao", "nome")
            )
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
                    Demanda.objects.filter(tipo=tipo).exclude(status=StatusDemanda.CONCLUIDA).exclude(pk__in=pks_set).update(priorizacao=None)
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "erro": str(e)}, status=400)
