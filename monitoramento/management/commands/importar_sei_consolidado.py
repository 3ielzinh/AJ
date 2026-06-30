from pathlib import Path
import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Min

from monitoramento.models import DocumentoSEI, ProcessoSEI


ARQUIVO_PADRAO = Path(
    r"C:\Users\gabriel.jorge\Documents\Codex\2026-06-24\vamo\outputs\sei-demandas-consolidadas\demandas_por_assunto.txt"
)


def _ler_texto_robusto(arquivo: Path) -> str:
    bruto = arquivo.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return bruto.decode(enc)
        except UnicodeDecodeError:
            continue
    return bruto.decode("utf-8", errors="replace")


def _normalizar_valor(valor: str) -> str:
    return (valor or "").strip()


def _parse_data_brasil(valor: str):
    if not valor:
        return None
    texto = str(valor).strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


def _carregar_mapa_datas_assinatura(arquivo_json: Path):
    if not arquivo_json.exists():
        return {}

    try:
        dados = json.loads(_ler_texto_robusto(arquivo_json))
    except Exception:
        return {}

    mapa = {}
    for item in dados.get("demandas", []):
        numero = _normalizar_valor(item.get("documento"))
        if not numero:
            continue

        datas = []
        for assinatura in item.get("assinaturas", []) or []:
            dt = _parse_data_brasil(assinatura.get("data"))
            if dt:
                datas.append(dt)

        if datas:
            mapa[numero] = min(datas)

    return mapa


class Command(BaseCommand):
    help = (
        "Importa o arquivo demandas_por_assunto.txt do SEI com foco processual: "
        "consolida processos e vincula documentos ao processo correspondente."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            type=str,
            default=str(ARQUIVO_PADRAO),
            help=f"Caminho do arquivo .txt consolidado (padrao: {ARQUIVO_PADRAO})",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            default=False,
            help="Remove processos e documentos atuais antes da importacao.",
        )
        parser.add_argument(
            "--arquivo-json",
            type=str,
            default="",
            help="Arquivo JSON consolidado para capturar datas de assinatura (opcional).",
        )

    def handle(self, *args, **options):
        arquivo = Path(options["arquivo"])
        if not arquivo.exists():
            raise CommandError(f"Arquivo nao encontrado: {arquivo}")

        texto = _ler_texto_robusto(arquivo)
        linhas = texto.splitlines()

        if options.get("arquivo_json"):
            arquivo_json = Path(options["arquivo_json"])
        else:
            arquivo_json = arquivo.with_name("demandas_consolidadas.json")
        mapa_datas_assinatura = _carregar_mapa_datas_assinatura(arquivo_json)

        if options["limpar"]:
            removidos_docs, _ = DocumentoSEI.objects.all().delete()
            removidos_proc, _ = ProcessoSEI.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Base limpa: {removidos_docs} documento(s), {removidos_proc} processo(s)."
                )
            )

        assunto_atual = ""
        in_resumo = False
        resumo_linhas = []
        atual = None

        total_processos_criados = 0
        total_processos_atualizados = 0
        total_docs_criados = 0
        total_docs_atualizados = 0
        total_docs_ignorados = 0
        total_docs_repetidos_no_txt = 0

        vistos_documentos = set()
        processos_tocados = set()

        def iniciar_documento():
            return {
                "numero_documento": "",
                "tipo": "",
                "processo": "",
                "unidade": "",
                "resumo": "",
                "assinantes": "",
                "criado_por": "",
                "versao_por": "",
                "arquivo_nome": "",
                "assunto": "",
            }

        def finalizar_documento(doc):
            nonlocal total_processos_criados
            nonlocal total_processos_atualizados
            nonlocal total_docs_criados
            nonlocal total_docs_atualizados
            nonlocal total_docs_ignorados
            nonlocal total_docs_repetidos_no_txt

            if not doc:
                return

            numero_documento = _normalizar_valor(doc.get("numero_documento", ""))
            numero_processo = _normalizar_valor(doc.get("processo", ""))

            if not numero_documento or not numero_processo:
                total_docs_ignorados += 1
                return

            if numero_documento in vistos_documentos:
                total_docs_repetidos_no_txt += 1
            vistos_documentos.add(numero_documento)

            processo_defaults = {
                "assunto_principal": _normalizar_valor(doc.get("assunto", "")),
                "unidade_principal": _normalizar_valor(doc.get("unidade", "")),
            }
            processo, criado_processo = ProcessoSEI.objects.update_or_create(
                numero_processo=numero_processo,
                defaults=processo_defaults,
            )
            processos_tocados.add(processo.pk)

            if criado_processo:
                total_processos_criados += 1
            else:
                total_processos_atualizados += 1

            doc_defaults = {
                "processo": processo,
                "assunto": _normalizar_valor(doc.get("assunto", "")),
                "tipo": _normalizar_valor(doc.get("tipo", "")),
                "data_assinatura": mapa_datas_assinatura.get(numero_documento),
                "unidade": _normalizar_valor(doc.get("unidade", "")),
                "resumo": _normalizar_valor(doc.get("resumo", "")),
                "assinantes": _normalizar_valor(doc.get("assinantes", "")),
                "criado_por": _normalizar_valor(doc.get("criado_por", "")),
                "versao_por": _normalizar_valor(doc.get("versao_por", "")),
                "arquivo_nome": _normalizar_valor(doc.get("arquivo_nome", "")),
            }
            _, criado_doc = DocumentoSEI.objects.update_or_create(
                numero_documento=numero_documento,
                defaults=doc_defaults,
            )
            if criado_doc:
                total_docs_criados += 1
            else:
                total_docs_atualizados += 1

        with transaction.atomic():
            for linha_raw in linhas:
                linha = linha_raw.strip()

                if linha.startswith("ASSUNTO:"):
                    if in_resumo and atual is not None:
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                    finalizar_documento(atual)
                    atual = None
                    assunto_atual = _normalizar_valor(linha.split(":", 1)[1])
                    continue

                if linha.startswith("Documento:"):
                    if in_resumo and atual is not None:
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                    finalizar_documento(atual)
                    atual = iniciar_documento()
                    atual["assunto"] = assunto_atual
                    atual["numero_documento"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue

                if atual is None:
                    continue

                if in_resumo:
                    if linha.startswith("Assinantes:"):
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                        atual["assinantes"] = _normalizar_valor(linha.split(":", 1)[1])
                        continue
                    if linha.startswith("Criado por:"):
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                        atual["criado_por"] = _normalizar_valor(linha.split(":", 1)[1])
                        continue
                    if linha.startswith("Versão por:") or linha.startswith("Versao por:"):
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                        atual["versao_por"] = _normalizar_valor(linha.split(":", 1)[1])
                        continue
                    if linha.startswith("Arquivo:"):
                        atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
                        resumo_linhas = []
                        in_resumo = False
                        atual["arquivo_nome"] = _normalizar_valor(linha.split(":", 1)[1])
                        continue
                    resumo_linhas.append(linha_raw.rstrip())
                    continue

                if linha.startswith("Tipo:"):
                    atual["tipo"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Processo:"):
                    atual["processo"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Unidade:"):
                    atual["unidade"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Resumo:"):
                    in_resumo = True
                    resumo_inicial = _normalizar_valor(linha.split(":", 1)[1])
                    resumo_linhas = [resumo_inicial] if resumo_inicial else []
                    continue
                if linha.startswith("Assinantes:"):
                    atual["assinantes"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Criado por:"):
                    atual["criado_por"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Versão por:") or linha.startswith("Versao por:"):
                    atual["versao_por"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue
                if linha.startswith("Arquivo:"):
                    atual["arquivo_nome"] = _normalizar_valor(linha.split(":", 1)[1])
                    continue

            if in_resumo and atual is not None:
                atual["resumo"] = "\n".join([l for l in resumo_linhas if l]).strip()
            finalizar_documento(atual)

            # Recalcula totais de documentos por processo.
            for item in ProcessoSEI.objects.annotate(total_calc=Count("documentos")):
                ProcessoSEI.objects.filter(pk=item.pk).update(total_documentos=item.total_calc)

            # Primeira data de assinatura por processo.
            for item in ProcessoSEI.objects.annotate(primeira_data=Min("documentos__data_assinatura")):
                ProcessoSEI.objects.filter(pk=item.pk).update(primeira_data_assinatura=item.primeira_data)

        self.stdout.write(
            self.style.SUCCESS(
                "Importacao SEI concluida: "
                f"{total_processos_criados} processo(s) criado(s), "
                f"{total_processos_atualizados} processo(s) atualizado(s), "
                f"{total_docs_criados} documento(s) criado(s), "
                f"{total_docs_atualizados} documento(s) atualizado(s), "
                f"{total_docs_ignorados} documento(s) ignorado(s), "
                f"{total_docs_repetidos_no_txt} repeticao(oes) de documento no arquivo."
            )
        )
