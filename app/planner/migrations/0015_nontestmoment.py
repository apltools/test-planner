# Generated by Django 2.2.7 on 2020-01-09 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0014_auto_20191129_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='NonTestMoment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=16, verbose_name='Locatie')),
                ('date', models.DateField(verbose_name='Datum')),
                ('start_time', models.TimeField(verbose_name='Begintijd')),
                ('end_time', models.TimeField(verbose_name='Eindtijd')),
                ('hidden_from_total', models.BooleanField(default=False, verbose_name='Verborgen')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
