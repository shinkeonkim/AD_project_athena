# Generated by Django 5.2.1 on 2025-05-26 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("article", "0004_remove_article_content_alter_article_author"),
    ]

    operations = [
        migrations.RenameField(
            model_name="article",
            old_name="problem_summary",
            new_name="summary",
        ),
    ]
