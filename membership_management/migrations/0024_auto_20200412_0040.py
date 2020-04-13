# Generated by Django 3.0.4 on 2020-04-12 04:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hotshot_web.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0023_auto_20200410_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='override_recurring_cycle_starts_on',
        ),
        migrations.CreateModel(
            name='AuxMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email address')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=16)),
                ('profile_pic', models.ImageField(blank=True, null=True, storage=hotshot_web.storage_backends.PrivateMediaStorage(), upload_to='profile_pic')),
                ('primary_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aux_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]