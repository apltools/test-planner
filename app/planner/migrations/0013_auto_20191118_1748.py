# Generated by Django 2.2.6 on 2019-11-18 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0012_coursemoment_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='test',
            options={'ordering': ('name',), 'verbose_name': 'Toetsje', 'verbose_name_plural': 'Toetsjes'},
        ),
    ]
