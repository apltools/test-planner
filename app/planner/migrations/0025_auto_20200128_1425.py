# Generated by Django 3.0.2 on 2020-01-28 14:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0024_auto_20200114_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(verbose_name='Datum'),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.TimeField(verbose_name='Eind Tijd'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.TimeField(verbose_name='Start Tijd'),
        ),
    ]
