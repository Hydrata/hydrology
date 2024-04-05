# Generated by Django 3.2.20 on 2024-04-05 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hydrology', '0008_alter_timeseries_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='idftable',
            name='chart',
            field=models.ImageField(blank=True, null=True, upload_to='idftable/chart/'),
        ),
        migrations.AddField(
            model_name='timeseries',
            name='chart',
            field=models.ImageField(blank=True, null=True, upload_to='timeseries/chart/'),
        ),
    ]
