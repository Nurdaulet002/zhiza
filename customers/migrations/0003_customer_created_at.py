# Generated by Django 3.2.4 on 2023-08-15 09:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
