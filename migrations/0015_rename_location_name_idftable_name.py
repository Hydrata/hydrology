# Generated by Django 3.2.20 on 2024-05-21 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hydrology', '0014_auto_20240518_0749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='idftable',
            old_name='location_name',
            new_name='name',
        ),
    ]
