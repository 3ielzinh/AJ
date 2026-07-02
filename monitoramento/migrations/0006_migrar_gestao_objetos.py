from decimal import Decimal, InvalidOperation
import unicodedata

from django.db import migrations


SIM_VALUES = {"SIM", "S", "TRUE", "1", "YES"}
NAO_VALUES = {"NAO", "N", "FALSE", "0", "NO"}


def normalize(value):
    text = str(value or "").strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.upper().split())


def parse_bool(value):
    normalized = normalize(value)
    if normalized in SIM_VALUES:
        return True
    if normalized in NAO_VALUES:
        return False
    return None


def parse_decimal(value):
    text = str(value or "").strip()
    if not text:
        return None
    text = text.replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_observacoes(text):
    dados = {}
    for line in str(text or "").splitlines():
        item = line.strip()
        if not item.startswith("- ") or ":" not in item:
            continue
        key, value = item[2:].split(":", 1)
        dados[normalize(key)] = value.strip()
    return dados


def to_int(value):
    try:
        return int(str(value or "").strip())
    except (TypeError, ValueError):
        return None


def migrar(apps, schema_editor):
    Demanda = apps.get_model("monitoramento", "Demanda")
    ObjetoGestao = apps.get_model("monitoramento", "ObjetoGestao")

    for demanda in Demanda.objects.filter(tipo="gestao_objetos").order_by("id"):
        dados = parse_observacoes(demanda.observacoes)
        defaults = {
            "id_objeto": dados.get("ID DO OBJETO", ""),
            "descricao": dados.get("DESCRICAO", ""),
            "grupo": demanda.classificacao or "",
            "ativo": parse_bool(dados.get("ATIVO", "")),
            "data_encerramento": demanda.data_conclusao,
            "processo_sei": demanda.processo_sei or "",
            "ajs_ativas": dados.get("AJS ATIVAS", ""),
            "tipo_objeto": dados.get("TIPO DE OBJETO", ""),
            "carater": dados.get("CARATER", ""),
            "fluxo_confirmacao": dados.get("FLUXO DE CONFIRMACAO", ""),
            "passivel_absorcao": parse_bool(dados.get("PASSIVEL DE ABSORCAO", "")),
            "tema": dados.get("TEMA", ""),
            "subtema": dados.get("SUBTEMA", ""),
            "pedido_inicial": dados.get("PEDIDO INICIAL", ""),
            "limite_maximo_objeto": parse_decimal(dados.get("LIMITE MAXIMO DO OBJETO", "")),
            "observacao": dados.get("OBSERVACAO ORIGINAL", demanda.observacoes or ""),
            "aba_origem": dados.get("ABA ORIGEM", ""),
            "linha_origem": to_int(dados.get("LINHA ORIGEM", "")),
            "demanda_origem_id": demanda.id,
        }
        ObjetoGestao.objects.update_or_create(
            nome=demanda.nome,
            grupo=demanda.classificacao or "",
            defaults=defaults,
        )


def reverter(apps, schema_editor):
    ObjetoGestao = apps.get_model("monitoramento", "ObjetoGestao")
    ObjetoGestao.objects.filter(demanda_origem__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("monitoramento", "0005_objetogestao"),
    ]

    operations = [
        migrations.RunPython(migrar, reverter),
    ]
