from datetime import date

from django.db import models


class TipoDemanda(models.TextChoices):
    EVOLUTIVA          = "evolutiva",          "Evolutiva"
    CORRETIVA          = "corretiva",          "Corretiva"
    INDICACAO_RUBRICA  = "indicacao_rubrica",  "Indicação de Rubrica"
    CRIACAO_OBJETO     = "criacao_objeto",     "Criação de Objeto"


class StatusDemanda(models.TextChoices):
    NAO_INICIADA = "nao_iniciada", "Não Iniciada"
    EM_ANDAMENTO = "em_andamento", "Em Andamento"
    CONCLUIDA    = "concluida",    "Concluída"


class Demanda(models.Model):
    """
    Representa uma demanda do módulo de Monitoramento CGPJU.

    O campo `tipo` discrimina a categoria da demanda (evolutiva, corretiva,
    indicação de rubrica ou criação de objeto), permitindo listagens e filtros
    independentes por área, sem necessidade de models separados.

    A regra de cálculo de prazo (originalmente fórmula Excel na col. E da
    planilha) é implementada como property `dias_espera`:
        - Concluída  → data_conclusao − data_inicio
        - Em Andamento → date.today() − data_inicio
        - Demais     → None
    """

    # ── Identificação ──────────────────────────────────────────────────────
    nome = models.CharField("Nome da demanda", max_length=2000)
    tipo = models.CharField(
        "Tipo",
        max_length=30,
        choices=TipoDemanda.choices,
        db_index=True,
    )
    # Classificação existe apenas em demandas evolutivas
    classificacao = models.CharField(
        "Classificação",
        max_length=200,
        blank=True,
        default="",
    )

    # ── Status e datas ─────────────────────────────────────────────────────
    status = models.CharField(
        "Status",
        max_length=20,
        choices=StatusDemanda.choices,
        default=StatusDemanda.NAO_INICIADA,
        db_index=True,
    )
    data_inicio = models.DateField("Data de início", null=True, blank=True)
    data_conclusao = models.DateField("Data de conclusão", null=True, blank=True)

    # ── Rastreabilidade ────────────────────────────────────────────────────
    processo_sei = models.CharField("Processo SEI", max_length=300, blank=True, default="")
    processo_relacionado = models.TextField("Processo relacionado", blank=True, default="")
    alm = models.CharField("ALM", max_length=100, blank=True, default="")
    localizacao = models.CharField("Localização", max_length=500, blank=True, default="")

    # ── Reiteração ─────────────────────────────────────────────────────────
    reiterada = models.BooleanField("Demanda reiterada", default=False)
    data_reiteracao = models.DateField("Data de reiteração", null=True, blank=True)

    # ── Prioridade e observações ───────────────────────────────────────────
    priorizacao = models.IntegerField("Priorização", null=True, blank=True)
    observacoes = models.TextField("Observações", blank=True, default="")

    # ── Auditoria ──────────────────────────────────────────────────────────
    criado_em    = models.DateTimeField("Criado em",    auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name         = "Demanda"
        verbose_name_plural  = "Demandas"
        ordering             = ["tipo", "priorizacao", "-criado_em"]
        indexes = [
            models.Index(fields=["tipo", "status"]),
            models.Index(fields=["data_inicio"]),
        ]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nome[:80]}"

    # ── Regra de negócio: cálculo de prazo ────────────────────────────────
    @property
    def dias_espera(self) -> int | None:
        """
        Calcula a quantidade de dias da demanda com base no status:
        - Concluída:    data_conclusao − data_inicio
        - Em Andamento: data_atual    − data_inicio
        - Demais:       None
        """
        if not self.data_inicio:
            return None
        if self.status == StatusDemanda.CONCLUIDA and self.data_conclusao:
            return (self.data_conclusao - self.data_inicio).days
        if self.status == StatusDemanda.EM_ANDAMENTO:
            return (date.today() - self.data_inicio).days
        return None

    @property
    def dias_espera_display(self) -> str:
        """Versão formatada de dias_espera para uso direto em templates."""
        d = self.dias_espera
        return str(d) if d is not None else "—"
