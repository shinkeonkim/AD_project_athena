# Generated by Django 5.2.1 on 2025-05-28 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agent", "0004_questiontaskrating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="questiontaskrating",
            name="message",
            field=models.TextField(blank=True, null=True),
        ),
    ]
