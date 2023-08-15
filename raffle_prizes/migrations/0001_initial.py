# Generated by Django 3.2.4 on 2023-08-15 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_request', '0001_initial'),
        ('organizations', '0002_branch_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='RafflePrize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('message_winner', models.TextField()),
                ('number_winners', models.PositiveIntegerField(default=1)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('comment', models.TextField()),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Разыграно'), (2, 'Не разыграно')], default=2)),
            ],
        ),
        migrations.CreateModel(
            name='Winner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_win', models.DateField(auto_now=True)),
                ('customer_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_request.customerrequest')),
                ('raffle_prize', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raffle_prizes.raffleprize')),
            ],
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promo_code', models.CharField(max_length=180, unique=True)),
                ('customer_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_request.customerrequest')),
                ('raffle_prize', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raffle_prizes.raffleprize')),
            ],
        ),
        migrations.CreateModel(
            name='ParticipatingBranch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.branch')),
                ('raffle_prize', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raffle_prizes.raffleprize')),
            ],
        ),
    ]
