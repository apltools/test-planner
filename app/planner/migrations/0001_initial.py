# Generated by Django 3.0.4 on 2020-03-15 14:06

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import planner.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_teaching_assistant', models.BooleanField(default=False, verbose_name='Assistent')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_slot_length', models.IntegerField(blank=True, null=True)),
                ('_location', models.CharField(blank=True, max_length=16, null=True)),
                ('_extras', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('_capacity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Capaciteit')),
                ('name', models.CharField(max_length=64, null=True, unique=True)),
                ('slug', models.SlugField(max_length=16, null=True, unique=True)),
                ('_host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_slot_length', models.IntegerField(blank=True, null=True)),
                ('_location', models.CharField(blank=True, max_length=16, null=True)),
                ('_extras', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('_capacity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Capaciteit')),
                ('date', models.DateField(verbose_name='Datum')),
                ('start_time', models.TimeField(verbose_name='Start Tijd')),
                ('end_time', models.TimeField(verbose_name='Eind Tijd')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('_host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='planner.EventType')),
            ],
            options={
                'ordering': ['-date', '-start_time'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventAppointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Naam')),
                ('student_nr', models.PositiveIntegerField(verbose_name='Studentnummer')),
                ('email', models.EmailField(max_length=254)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cancel_secret', models.CharField(default=planner.models.gen_cancel_secret, max_length=64, unique=True)),
                ('extras', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='planner.Event')),
            ],
            options={
                'ordering': ['date', 'start_time'],
                'unique_together': {('student_nr', 'date')},
            },
        ),
    ]
