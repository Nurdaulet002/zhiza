# Generated by Django 3.2.4 on 2023-08-28 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20230827_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='code',
            field=models.CharField(max_length=6, null=True, unique=True),
        ),
    ]
