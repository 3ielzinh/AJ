from django.db import migrations, models


def unifica_tipos_para_gestao_objetos(apps, schema_editor):
    Demanda = apps.get_model("monitoramento", "Demanda")
    Demanda.objects.filter(tipo__in=["indicacao_rubrica", "criacao_objeto"]).update(
        tipo="gestao_objetos"
    )


def desfaz_unificacao_tipos(apps, schema_editor):
    # Nao existe informacao suficiente para separar com seguranca os registros
    # que eram "indicacao_rubrica" dos que eram "criacao_objeto".
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("monitoramento", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(unifica_tipos_para_gestao_objetos, desfaz_unificacao_tipos),
        migrations.AlterField(
            model_name="demanda",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("evolutiva", "Evolutiva"),
                    ("corretiva", "Corretiva"),
                    ("gestao_objetos", "Gestão de Objetos"),
                ],
                db_index=True,
                max_length=30,
                verbose_name="Tipo",
            ),
        ),
    ]
