# Generated by Django 3.0.4 on 2020-04-03 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership_management', '0013_membership_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['display_order']},
        ),
    ]
