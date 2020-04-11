# Generated by Django 3.0.4 on 2020-04-10 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0019_auto_20200404_2357'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profiles'),
        ),
        migrations.AlterField(
            model_name='member',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='members', to='membership_management.Membership'),
        ),
        migrations.AlterField(
            model_name='member',
            name='membership_expiration',
            field=models.DateField(blank=True, null=True),
        ),
    ]
