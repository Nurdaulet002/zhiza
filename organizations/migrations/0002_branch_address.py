# Generated by Django 3.2.4 on 2023-08-14 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='address',
            field=models.CharField(blank=True, max_length=180, null=True),
        ),
    ]
