# Generated by Django 3.2.4 on 2023-07-27 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('text', models.TextField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Черновик'), (2, 'На проверке'), (3, 'Готовы к запуску'), (4, 'Остановлены'), (5, 'Выполняются'), (6, 'Завершённые'), (7, 'Удалённые')], default=1)),
                ('total_customers', models.PositiveIntegerField(blank=True, null=True)),
                ('total_getting_customers', models.PositiveIntegerField(blank=True, null=True)),
                ('active_last_month', models.BooleanField(default=False)),
                ('active_last_week', models.BooleanField(default=False)),
                ('active_last_day', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BranchNewsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.branch')),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.newsletter')),
            ],
        ),
    ]
