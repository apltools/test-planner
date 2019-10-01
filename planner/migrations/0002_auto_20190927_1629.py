# Generated by Django 2.2.5 on 2019-09-27 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appointment',
            options={'verbose_name': 'Appointment', 'verbose_name_plural': 'Appointments'},
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='time',
            new_name='start_time',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='student_name',
            field=models.CharField(max_length=32, verbose_name='Name'),
        ),
    ]
