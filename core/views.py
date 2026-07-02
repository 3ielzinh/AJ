import csv
from datetime import datetime
import re

from django.views.generic import TemplateView
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
import unicodedata

from monitoramento.models import Demanda, DocumentoSEI, ObjetoGestao, StatusDemanda, TipoDemanda
from .forms import SignUpForm


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        total_demandas = Demanda.objects.count()
        concluidas = Demanda.objects.filter(status=StatusDemanda.CONCLUIDA).count()
        em_andamento = Demanda.objects.filter(status=StatusDemanda.EM_ANDAMENTO).count()
        nao_iniciadas = Demanda.objects.filter(status=StatusDemanda.NAO_INICIADA).count()

        taxa_conclusao = round((concluidas / total_demandas) * 100) if total_demandas else 0

        ctx.update(
            {
                "total_demandas": total_demandas,
                "total_concluidas": concluidas,
                "total_em_andamento": em_andamento,
                "total_nao_iniciadas": nao_iniciadas,
                "taxa_conclusao": taxa_conclusao,
                "total_processos_sei": DocumentoSEI.objects.values("processo").distinct().count(),
                "total_documentos_sei": DocumentoSEI.objects.count(),
                "total_corretivas": Demanda.objects.filter(tipo=TipoDemanda.CORRETIVA).count(),
                "total_evolutivas": Demanda.objects.filter(tipo=TipoDemanda.EVOLUTIVA).count(),
                "total_gestao_objetos": ObjetoGestao.objects.count(),
            }
        )
        return ctx


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "core/perfil.html"

    PARTICIPACAO_MAP = {
        "criacao": "Criacao",
        "edicao": "Edicao",
        "analise": "Analise",
        "assinatura": "Assinatura",
    }

    @staticmethod
    def _normalize_text(value: str) -> str:
        text = (value or "").strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return " ".join(text.split())

    @staticmethod
    def _build_identity(user):
        username = ProfileView._normalize_text(user.username or "")
        full_name = ProfileView._normalize_text((user.get_full_name() or user.first_name or ""))
        username_as_name = ProfileView._normalize_text((user.username or "").replace(".", " "))
        return {
            "username": username,
            "full_name": full_name,
            "username_as_name": username_as_name,
        }

    @staticmethod
    def _matches_authorship(value: str, identity: dict) -> bool:
        raw = (value or "").strip()
        if not raw:
            return False

        normalized = ProfileView._normalize_text(raw)
        local_part = ProfileView._normalize_text(raw.split("@", 1)[0]) if "@" in raw else normalized

        if identity["username"] and (normalized == identity["username"] or local_part == identity["username"]):
            return True

        if identity["full_name"] and normalized == identity["full_name"]:
            return True

        return False

    @staticmethod
    def _matches_signature(value: str, identity: dict) -> bool:
        if not value:
            return False

        entries = [e.strip() for e in str(value).split(";") if e.strip()]
        candidate_names = {
            identity["full_name"],
            identity["username_as_name"],
        }
        candidate_names = {c for c in candidate_names if c}

        for entry in entries:
            signer_name = entry.split(" - ", 1)[0].strip()
            signer_norm = ProfileView._normalize_text(signer_name)
            if signer_norm in candidate_names:
                return True
        return False

    @staticmethod
    def _is_analysis_type(tipo: str) -> bool:
        normalized = ProfileView._normalize_text(tipo or "")
        return any(k in normalized for k in ("nota", "parecer", "analise"))

    @classmethod
    def _build_participacao_counts(cls, matched_docs):
        criacao_ids = set()
        edicao_ids = set()
        analise_ids = set()
        assinatura_ids = set()

        for item in matched_docs:
            doc_id = item["doc"].id
            roles = set(item["roles"])
            if "Criacao" in roles:
                criacao_ids.add(doc_id)
            if "Edicao" in roles:
                edicao_ids.add(doc_id)
            if "Analise" in roles:
                analise_ids.add(doc_id)
            if "Assinatura" in roles:
                assinatura_ids.add(doc_id)

        return {
            "criacao": len(criacao_ids),
            "edicao": len(edicao_ids),
            "analise": len(analise_ids),
            "assinatura": len(assinatura_ids),
            "total": len(matched_docs),
        }

    @classmethod
    def _matches_free_text(cls, item, termo_norm: str) -> bool:
        doc = item["doc"]
        campos = [
            doc.numero_documento,
            doc.processo.numero_processo if doc.processo else "",
            doc.tipo,
            doc.assunto,
            doc.unidade,
            doc.resumo,
            doc.assinantes,
            doc.criado_por,
            doc.versao_por,
            doc.arquivo_nome,
            " ".join(item["roles"]),
        ]

        for campo in campos:
            if termo_norm in cls._normalize_text(str(campo or "")):
                return True
        return False

    @classmethod
    def _collect_user_documents(cls, user, termo="", participacao="", mes_ano=""):
        identity = cls._build_identity(user)

        all_docs = DocumentoSEI.objects.select_related("processo").order_by("-data_assinatura", "-atualizado_em", "-id")
        matched_docs = []

        for doc in all_docs:
            roles = []
            created_match = cls._matches_authorship(doc.criado_por, identity)
            edited_match = cls._matches_authorship(doc.versao_por, identity)
            signed_match = cls._matches_signature(doc.assinantes, identity)
            analysis_match = (created_match or edited_match or signed_match) and cls._is_analysis_type(doc.tipo)

            if created_match:
                roles.append("Criacao")
            if edited_match:
                roles.append("Edicao")
            if analysis_match:
                roles.append("Analise")
            if signed_match:
                roles.append("Assinatura")

            if roles:
                matched_docs.append({"doc": doc, "roles": roles})

        termo_norm = cls._normalize_text(termo or "")
        if termo_norm:
            matched_docs = [item for item in matched_docs if cls._matches_free_text(item, termo_norm)]

        role_filter = cls.PARTICIPACAO_MAP.get((participacao or "").strip().lower())
        if role_filter:
            matched_docs = [item for item in matched_docs if role_filter in item["roles"]]

        if mes_ano:
            try:
                ano, mes = [int(p) for p in mes_ano.split("-", 1)]
            except (TypeError, ValueError):
                ano, mes = None, None

            if ano and mes:
                matched_docs = [
                    item
                    for item in matched_docs
                    if item["doc"].data_assinatura
                    and item["doc"].data_assinatura.year == ano
                    and item["doc"].data_assinatura.month == mes
                ]

        participacao = cls._build_participacao_counts(matched_docs)
        return matched_docs, participacao

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        termo = (self.request.GET.get("q") or "").strip()
        filtro_participacao = (self.request.GET.get("participacao") or "").strip().lower()
        filtro_mes_ano = (self.request.GET.get("mes_ano") or "").strip()

        matched_docs, participacao = self._collect_user_documents(
            self.request.user,
            termo=termo,
            participacao=filtro_participacao,
            mes_ano=filtro_mes_ano,
        )

        paginator = Paginator(matched_docs, 20)
        page_obj = paginator.get_page(self.request.GET.get("page", 1))

        query_params = self.request.GET.copy()
        if "page" in query_params:
            query_params.pop("page")
        querystring = query_params.urlencode()

        ctx["participacao"] = participacao
        ctx["docs_page"] = page_obj
        ctx["docs_with_roles"] = page_obj.object_list
        ctx["filtro_q"] = termo
        ctx["filtro_participacao"] = filtro_participacao
        ctx["filtro_mes_ano"] = filtro_mes_ano
        ctx["filtros_ativos"] = bool(termo or filtro_participacao or filtro_mes_ano)
        ctx["querystring"] = querystring
        ctx["export_querystring"] = querystring
        ctx["participacao_opcoes"] = [
            ("", "Todas participações"),
            ("criacao", "Criação"),
            ("edicao", "Edição"),
            ("analise", "Análise"),
            ("assinatura", "Assinatura"),
        ]
        return ctx


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


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("core:home")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def export_profile_documents_csv(request):
    termo = (request.GET.get("q") or "").strip()
    filtro_participacao = (request.GET.get("participacao") or "").strip().lower()
    filtro_mes_ano = (request.GET.get("mes_ano") or "").strip()

    matched_docs, _ = ProfileView._collect_user_documents(
        request.user,
        termo=termo,
        participacao=filtro_participacao,
        mes_ano=filtro_mes_ano,
    )

    filename = f"perfil_documentos_{request.user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # BOM para abrir acentuacao corretamente no Excel.
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")

    def _csv_text(value):
        # Evita quebras de linha no Excel e reduz espacos repetidos.
        texto = str(value or "")
        texto = texto.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        return re.sub(r"\s+", " ", texto).strip()

    writer.writerow([
        "documento",
        "processo",
        "data_assinatura",
        "tipo",
        "assunto",
        "unidade",
        "resumo",
        "assinantes",
        "criado_por",
        "versao_por",
        "arquivo",
        "participacoes",
    ])

    for item in matched_docs:
        doc = item["doc"]
        roles = ", ".join(item["roles"])
        writer.writerow([
            _csv_text(doc.numero_documento),
            _csv_text(doc.processo.numero_processo if doc.processo else ""),
            doc.data_assinatura.strftime("%d/%m/%Y") if doc.data_assinatura else "",
            _csv_text(doc.tipo),
            _csv_text(doc.assunto),
            _csv_text(doc.unidade),
            _csv_text(doc.resumo),
            _csv_text(doc.assinantes),
            _csv_text(doc.criado_por),
            _csv_text(doc.versao_por),
            _csv_text(doc.arquivo_nome),
            _csv_text(roles),
        ])

    return response
