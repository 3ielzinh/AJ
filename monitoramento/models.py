from datetime import date

from django.db import models


class TipoDemanda(models.TextChoices):
    EVOLUTIVA        = "evolutiva",        "Evolutiva"
    CORRETIVA        = "corretiva",        "Corretiva"
    GESTAO_OBJETOS   = "gestao_objetos",   "Gestão de Objetos"


class StatusDemanda(models.TextChoices):
    NAO_INICIADA = "nao_iniciada", "Não Iniciada"
    EM_ANDAMENTO = "em_andamento", "Em Andamento"
    CONCLUIDA    = "concluida",    "Concluída"


class Demanda(models.Model):
    """
    Representa uma demanda do módulo de Monitoramento CGPJU.

    O campo `tipo` discrimina a categoria da demanda (evolutiva, corretiva
    ou gestão de objetos), permitindo listagens e filtros
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


class ObjetoGestao(models.Model):
    """
    Catalogo operacional de objetos judiciais.

    Diferente de `Demanda`, este model representa itens de referencia da aba
    Gestao de Objetos, com campos proprios para filtragem, edicao e consulta.
    """

    id_objeto = models.CharField("ID do objeto", max_length=80, blank=True, default="", db_index=True)
    nome = models.CharField("Nome do objeto", max_length=2000, db_index=True)
    descricao = models.TextField("Descricao", blank=True, default="")
    grupo = models.CharField("Grupo de objetos", max_length=300, blank=True, default="", db_index=True)
    ativo = models.BooleanField("Ativo", null=True, blank=True, db_index=True)
    data_encerramento = models.DateField("Data de encerramento", null=True, blank=True)
    processo_sei = models.CharField("Processo SEI", max_length=300, blank=True, default="")
    ajs_ativas = models.TextField("AJs ativas", blank=True, default="")
    tipo_objeto = models.CharField("Tipo de objeto", max_length=300, blank=True, default="")
    carater = models.CharField("Carater", max_length=200, blank=True, default="", db_index=True)
    fluxo_confirmacao = models.CharField("Fluxo de confirmacao", max_length=300, blank=True, default="", db_index=True)
    passivel_absorcao = models.BooleanField("Passivel de absorcao", null=True, blank=True)
    tema = models.CharField("Tema", max_length=500, blank=True, default="", db_index=True)
    subtema = models.CharField("Subtema", max_length=500, blank=True, default="")
    pedido_inicial = models.TextField("Pedido inicial", blank=True, default="")
    limite_maximo_objeto = models.DecimalField(
        "Limite maximo do objeto",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    observacao = models.TextField("Observacao", blank=True, default="")
    aba_origem = models.CharField("Aba de origem", max_length=200, blank=True, default="")
    linha_origem = models.PositiveIntegerField("Linha de origem", null=True, blank=True)
    demanda_origem = models.ForeignKey(
        Demanda,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="objetos_gestao_migrados",
        verbose_name="Demanda de origem",
    )
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Objeto de Gestao"
        verbose_name_plural = "Objetos de Gestao"
        ordering = ["grupo", "nome"]
        indexes = [
            models.Index(fields=["grupo", "ativo"]),
            models.Index(fields=["carater", "fluxo_confirmacao"]),
            models.Index(fields=["tema"]),
        ]

    def __str__(self):
        return self.nome[:120]

    @property
    def ativo_display(self) -> str:
        if self.ativo is True:
            return "Sim"
        if self.ativo is False:
            return "Nao"
        return "Nao informado"

    @property
    def passivel_absorcao_display(self) -> str:
        if self.passivel_absorcao is True:
            return "Sim"
        if self.passivel_absorcao is False:
            return "Nao"
        return "Nao informado"


class ProcessoSEI(models.Model):
    numero_processo = models.CharField("Processo SEI", max_length=30, unique=True, db_index=True)
    assunto_principal = models.CharField("Assunto principal", max_length=2000, blank=True, default="")
    unidade_principal = models.CharField("Unidade principal", max_length=300, blank=True, default="")
    primeira_data_assinatura = models.DateField("Primeira data de assinatura", null=True, blank=True)
    total_documentos = models.PositiveIntegerField("Total de documentos", default=0)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Processo SEI"
        verbose_name_plural = "Processos SEI"
        ordering = ["numero_processo"]
        indexes = [
            models.Index(fields=["numero_processo"]),
            models.Index(fields=["assunto_principal"]),
        ]

    def __str__(self):
        return self.numero_processo


class DocumentoSEI(models.Model):
    processo = models.ForeignKey(
        ProcessoSEI,
        on_delete=models.CASCADE,
        related_name="documentos",
        verbose_name="Processo",
    )
    numero_documento = models.CharField("Documento", max_length=20, unique=True, db_index=True)
    assunto = models.CharField("Assunto", max_length=2000, blank=True, default="")
    tipo = models.CharField("Tipo", max_length=200, blank=True, default="")
    data_assinatura = models.DateField("Data de assinatura", null=True, blank=True)
    unidade = models.CharField("Unidade", max_length=300, blank=True, default="")
    resumo = models.TextField("Resumo", blank=True, default="")
    assinantes = models.TextField("Assinantes", blank=True, default="")
    criado_por = models.CharField("Criado por", max_length=255, blank=True, default="")
    versao_por = models.CharField("Versão por", max_length=255, blank=True, default="")
    arquivo_nome = models.CharField("Arquivo", max_length=500, blank=True, default="")
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Documento SEI"
        verbose_name_plural = "Documentos SEI"
        ordering = ["numero_documento"]
        indexes = [
            models.Index(fields=["processo", "numero_documento"]),
            models.Index(fields=["tipo"]),
        ]

    def __str__(self):
        return f"{self.numero_documento} ({self.processo.numero_processo})"
