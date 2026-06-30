from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoramento", "0003_processosei_documentosei"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentosei",
            name="data_assinatura",
            field=models.DateField(blank=True, null=True, verbose_name="Data de assinatura"),
        ),
        migrations.AddField(
            model_name="processosei",
            name="primeira_data_assinatura",
            field=models.DateField(blank=True, null=True, verbose_name="Primeira data de assinatura"),
        ),
    ]
