# Generated by Django 2.2.6 on 2019-10-28 12:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0008_auto_20191026_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmoment',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
