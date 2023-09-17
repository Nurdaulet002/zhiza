# Generated by Django 3.2.4 on 2023-09-17 11:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0002_remove_integration_branch'),
        ('organizations', '0006_branch_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='integration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='integrations.integration'),
        ),
    ]
