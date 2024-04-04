# Generated by Django 3.2.20 on 2024-04-04 10:19

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hydrology', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeseries',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timeseries',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeseries_created', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='timeseries',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AddField(
            model_name='timeseries',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeseries_updated', to=settings.AUTH_USER_MODEL, verbose_name='Updated by'),
        ),
        migrations.CreateModel(
            name='IDFTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('location_name', models.CharField(max_length=500)),
                ('location_geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('source', models.CharField(max_length=500)),
                ('notes', models.TextField(blank=True, null=True)),
                ('durations_in_mins', models.JSONField(blank=True, null=True, verbose_name='Durations in Minutes')),
                ('ey_12', models.JSONField(blank=True, null=True, verbose_name='12EY')),
                ('ey_6', models.JSONField(blank=True, null=True, verbose_name='6EY')),
                ('ey_4', models.JSONField(blank=True, null=True, verbose_name='4EY')),
                ('ey_3', models.JSONField(blank=True, null=True, verbose_name='3EY')),
                ('ey_2', models.JSONField(blank=True, null=True, verbose_name='2EY')),
                ('ey_1', models.JSONField(blank=True, null=True, verbose_name='1EY')),
                ('percent_50', models.JSONField(blank=True, null=True, verbose_name='50%')),
                ('ey_0_5', models.JSONField(blank=True, null=True, verbose_name='0.5EY')),
                ('percent_20', models.JSONField(blank=True, null=True, verbose_name='20%')),
                ('ey_0_2', models.JSONField(blank=True, null=True, verbose_name='0.2EY')),
                ('percent_10', models.JSONField(blank=True, null=True, verbose_name='10%')),
                ('percent_5', models.JSONField(blank=True, null=True, verbose_name='5%')),
                ('percent_2', models.JSONField(blank=True, null=True, verbose_name='2%')),
                ('percent_1', models.JSONField(blank=True, null=True, verbose_name='1%')),
                ('percent_0_5', models.JSONField(blank=True, null=True, verbose_name='0.5%')),
                ('percent_0_2', models.JSONField(blank=True, null=True, verbose_name='0.2%')),
                ('percent_0_01', models.JSONField(blank=True, null=True, verbose_name='0.01%')),
                ('percent_0_05', models.JSONField(blank=True, null=True, verbose_name='0.05%')),
                ('percent_0_002', models.JSONField(blank=True, null=True, verbose_name='0.02%')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='idf_table_created', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='idf_table_updated', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'verbose_name': 'IDF Table',
                'verbose_name_plural': 'IDF Tables',
            },
        ),
    ]
