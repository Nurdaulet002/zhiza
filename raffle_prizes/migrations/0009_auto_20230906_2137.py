# Generated by Django 3.2.4 on 2023-09-06 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raffle_prizes', '0008_alter_promocode_raffle_prize'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocode',
            name='raffle_prize',
        ),
        migrations.AddField(
            model_name='promocode',
            name='winner',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='raffle_prizes.winner'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='winner',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Выдан'), (2, 'Не выдан')], default=2),
        ),
    ]
