from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoramento", "0002_unifica_tipos_gestao_objetos"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessoSEI",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_processo", models.CharField(db_index=True, max_length=30, unique=True, verbose_name="Processo SEI")),
                ("assunto_principal", models.CharField(blank=True, default="", max_length=2000, verbose_name="Assunto principal")),
                ("unidade_principal", models.CharField(blank=True, default="", max_length=300, verbose_name="Unidade principal")),
                ("total_documentos", models.PositiveIntegerField(default=0, verbose_name="Total de documentos")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("atualizado_em", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
            ],
            options={
                "verbose_name": "Processo SEI",
                "verbose_name_plural": "Processos SEI",
                "ordering": ["numero_processo"],
                "indexes": [
                    models.Index(fields=["numero_processo"], name="monitoramen_numero__4dcf0d_idx"),
                    models.Index(fields=["assunto_principal"], name="monitoramen_assunto_102f99_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DocumentoSEI",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_documento", models.CharField(db_index=True, max_length=20, unique=True, verbose_name="Documento")),
                ("assunto", models.CharField(blank=True, default="", max_length=2000, verbose_name="Assunto")),
                ("tipo", models.CharField(blank=True, default="", max_length=200, verbose_name="Tipo")),
                ("unidade", models.CharField(blank=True, default="", max_length=300, verbose_name="Unidade")),
                ("resumo", models.TextField(blank=True, default="", verbose_name="Resumo")),
                ("assinantes", models.TextField(blank=True, default="", verbose_name="Assinantes")),
                ("criado_por", models.CharField(blank=True, default="", max_length=255, verbose_name="Criado por")),
                ("versao_por", models.CharField(blank=True, default="", max_length=255, verbose_name="Versão por")),
                ("arquivo_nome", models.CharField(blank=True, default="", max_length=500, verbose_name="Arquivo")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("atualizado_em", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
                (
                    "processo",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="documentos", to="monitoramento.processosei", verbose_name="Processo"),
                ),
            ],
            options={
                "verbose_name": "Documento SEI",
                "verbose_name_plural": "Documentos SEI",
                "ordering": ["numero_documento"],
                "indexes": [
                    models.Index(fields=["processo", "numero_documento"], name="monitoramen_processo_e2004d_idx"),
                    models.Index(fields=["tipo"], name="monitoramen_tipo_599dfb_idx"),
                ],
            },
        ),
    ]
