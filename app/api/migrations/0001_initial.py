# Generated by Django 3.0.3 on 2020-02-22 16:41

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIkey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=api.models.generate_api_key, max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
