# Generated by Django 3.0.4 on 2020-04-10 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0020_auto_20200410_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pic'),
        ),
    ]