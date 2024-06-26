# Generated by Django 3.2.20 on 2024-05-17 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hydrology', '0011_auto_20240506_0709'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='timeseries',
            name='hydrology_t_data_2dd622_gin',
        ),
        migrations.RemoveIndex(
            model_name='timeseries',
            name='hydrology_t_timezon_00dc62_idx',
        ),
        migrations.AlterField(
            model_name='timeseries',
            name='data',
            field=models.FileField(blank=True, null=True, upload_to='timeseries/data/'),
        ),
    ]
