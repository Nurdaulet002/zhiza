# Generated by Django 3.2.4 on 2023-08-29 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_alter_rating_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
