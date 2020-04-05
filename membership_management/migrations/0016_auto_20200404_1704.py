# Generated by Django 3.0.4 on 2020-04-04 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0015_auto_20200404_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='is_displayed',
            field=models.BooleanField(default=True, verbose_name='Is displayed on the website for customer to purchase'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_processor_id',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
