# Generated by Django 3.0.4 on 2020-04-02 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0010_auto_20200402_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='banner_message',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
