# Generated by Django 3.2.4 on 2023-09-02 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raffle_prizes', '0006_alter_winner_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffleprize',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='raffle_prizes/'),
        ),
    ]