# Generated by Django 3.0.2 on 2020-01-14 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0019_auto_20200114_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtype',
            name='name',
            field=models.CharField(max_length=16, null=True, unique=True),
        ),
    ]
