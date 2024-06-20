import copy
import json
import os
import tempfile

import pytz
import math
import matplotlib.pyplot as plt
import pystac
import uuid

from django.contrib.gis.db.models import PointField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from datetime import datetime
from django.core.files import File
from io import BytesIO

from gn_anuga.models import Project
from gn_anuga.storage_backends import AnugaDataStorage

User = get_user_model()


class TimeSeries(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_created', verbose_name="Created by")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_owner', verbose_name="Owner")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=500)
    source = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location_name = models.CharField(max_length=500, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC', choices=[(tz, tz) for tz in pytz.all_timezones])
    data = JSONField(default=list(), blank=True, null=True)
    stac = models.FileField(storage=AnugaDataStorage(), upload_to='timeseries/stac/', blank=True, null=True)
    chart = models.ImageField(storage=AnugaDataStorage(), upload_to='timeseries/chart/', blank=True, null=True)

    def __str__(self):
        if self.project:
            time_series_name = f"{self.project.name}_{self.id}_{self.name}".replace(" ", "_")
        else:
            time_series_name = f"None_{self.id}_{self.name}".replace(" ", "_")
        return time_series_name

    def clean(self):
        required_keys = {'timestamp', 'value'}
        for row_index, row in enumerate(self.data.get('rowData')):
            if not required_keys.issubset(row.keys()):
                raise ValidationError(f"The {required_keys} fields are required in each data point.")

            timestamp_string = row.get('timestamp')
            if timestamp_string.endswith('Z'):
                timestamp_string = timestamp_string.rstrip('Z')
                row['timestamp'] = timestamp_string

            try:
                datetime.fromisoformat(timestamp_string)
            except ValueError:
                raise ValidationError("All timestamps must be in ISO 8601 format.")

        if self.stac:
            contents = self.stac.read().decode()
            stac_dict = json.loads(contents)
            catalog = pystac.Catalog.from_dict(stac_dict)
            catalog.validate()

        if self.timezone not in pytz.all_timezones:
            raise ValidationError("The 'timezone' field must contain a valid timezone.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.create_chart(save=False)
        super().save(*args, **kwargs)

    def import_stac_from_simple_array(self, time_series_list):
        catalog = pystac.Catalog(
            id=uuid.uuid4().hex,
            description='desc',
            title='title'
        )

        extent = pystac.Extent(
            spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
            temporal=pystac.TemporalExtent([
                datetime.fromisoformat(time_series_list[0].get('timestamp')),
                datetime.fromisoformat(time_series_list[-1].get('timestamp'))
            ])
        )

        collection = pystac.Collection(
            id=uuid.uuid4().hex,
            description='Collection Description',
            extent=extent,
            title='title',
        )

        for item_inputs in time_series_list:
            item = pystac.Item(
                id=uuid.uuid4().hex,
                geometry=dict(),
                bbox=None,
                datetime=datetime.fromisoformat(item_inputs['timestamp']),
                properties={
                    'value': item_inputs['value'],
                    'unit': 'mm/hr'
                }
            )
            collection.add_item(item)
        catalog.add_child(collection)
        catalog_type = pystac.CatalogType("SELF_CONTAINED")
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = os.path.join(temp_dir, "catalog.json")
            catalog.normalize_and_save(catalog_path, catalog_type)
            self.stac.save(f"{self}/catalog.json", File(open(catalog_path, 'rb')))

    @property
    def data_with_datetimes(self):
        data_with_datetimes = []
        tz = pytz.timezone(self.timezone)
        for data_point in self.data.get('rowData'):
            data_point_copy = data_point.copy()
            data_point_copy['timestamp'] = datetime.fromisoformat(data_point['timestamp'].rstrip('Z')).replace(tzinfo=tz)
            data_with_datetimes.append(data_point_copy)
        return data_with_datetimes

    def create_chart(self, save=True):
        filename = f'{self.name}.png'
        timestamps = [item['timestamp'] for item in self.data.get('rowData')]
        values = [str(item['value']) for item in self.data.get('rowData')]
        plt.bar(timestamps, values)
        plt.tight_layout()  # Adjust layout to prevent cut-off

        # Save it to a BytesIO object
        file_buffer = BytesIO()
        plt.savefig(file_buffer, format='png')
        file_buffer.seek(0)
        self.chart.save(filename, File(file_buffer, name=filename), save=save)


class IDFTable(models.Model):
    MM = 'mm'
    CM = 'cm'
    IN = 'in'
    UNIT_CHOICES = [
        (MM, 'Millimeters'),
        (CM, 'Centimeters'),
        (IN, 'Inches'),
    ]
    UNIT_CONVERSIONS = {
        MM: 1,
        CM: 10,
        IN: 25.4,
    }

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='idf_table_created', verbose_name="Created by")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='idf_table_owner', verbose_name="Owner")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='idf_table_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=500)
    source = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location_geom = PointField(blank=True, null=True)
    data = JSONField(default=dict())
    original_units = models.CharField(max_length=4, choices=UNIT_CHOICES, default='mm')
    saved_units = models.CharField(max_length=4, choices=UNIT_CHOICES, default='mm')
    conversion_complete = models.BooleanField(default=False)
    selected_durations = JSONField("Selected Durations", blank=True, null=True)
    selected_frequencies = JSONField("Selected Frequencies", blank=True, null=True)

    def convert_to_mm(self):
        print('converting')
        for row in self.data.get('rowData'):
            for key in row:
                if "ARI" in key:
                    row[key] *= 1 # self.UNIT_CONVERSIONS[self.original_units]
        self.conversion_complete = True
        if self.id:
            self.save(update_fields=['data', 'conversion_complete'])

    def clean(self):
        if not isinstance(self.data, dict):
            raise ValidationError("Not a dictionary.")

        if not set(self.data.keys()).issuperset({"columnDefs", "rowData"}):
            raise ValidationError("Missing key(s) columnDefs and/or rowData")

        for i, column in enumerate(self.data.get('columnDefs')):
            if not isinstance(column, dict):
                raise ValidationError(f"columnDefs element at index {i} is not a dictionary.")

        for i, row in enumerate(self.data.get('rowData')):
            if not isinstance(row, dict):
                raise ValidationError(f"rowData element at index {i} is not a dict.")

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.original_units != 'mm' and not self.conversion_complete:
            self.convert_to_mm()
        super().save(*args, **kwargs)

    @staticmethod
    def ari_from_aep(aep):
        if aep > 100:
            raise ValidationError('AEP should be less than 100%')
        return -(1 / (math.log(1 - aep/100)))

    @staticmethod
    def aep_from_ari(ari):
        return 100 * (1 - math.exp((-1/ari)))

    def create_timeseries(self, duration_in_minutes, frequency, temporal_pattern, user=None):
        intensities = next((row for row in self.data.get('rowData') if row.get('duration') == duration_in_minutes), None)
        intensity = intensities.get(frequency, None)
        total_depth_value = intensity * duration_in_minutes / 60
        timeseries_data = list()
        temporal_pattern = temporal_pattern.data.get('rowData')
        timestep_in_seconds = 60 * (duration_in_minutes / len(temporal_pattern))

        for index, relative_proportion in enumerate(temporal_pattern):
            current_timestamp_python = datetime.fromtimestamp(index * timestep_in_seconds, pytz.UTC)
            current_timestamp_iso8601 = current_timestamp_python.isoformat()
            timeseries_data.append({
                'ts': current_timestamp_iso8601,
                'value': total_depth_value * relative_proportion
            })

        # Add the final timestamp to ensure we have a timeseries the same duration as duration_in_minutes
        final_index = len(temporal_pattern)
        current_timestamp_python = datetime.fromtimestamp(final_index * timestep_in_seconds, pytz.UTC)
        current_timestamp_iso8601 = current_timestamp_python.isoformat()
        timeseries_data.append({
            'ts': current_timestamp_iso8601,
            'value': total_depth_value * temporal_pattern[-1]
        })

        timeseries = TimeSeries.objects.create(
            name=f"{self.name} - {frequency} - {duration_in_minutes} minutes",
            data=timeseries_data,
            created_by=user
        )
        return timeseries

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "IDF Table"
        verbose_name_plural = "IDF Tables"


class TemporalPattern(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temporal_pattern_created', verbose_name="Created by")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temporal_pattern_owner', verbose_name="Owner")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temporal_pattern_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=500)
    source = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    data = JSONField("Pattern", blank=True, null=True)

    def clean(self):
        if self.data:
            row_data = self.data.get('rowData')
            if row_data:
                total_percentage = sum(d['percentage'] for d in row_data)
                if total_percentage != 100:
                    raise ValidationError("The sum of percentage values in the temporal pattern must sum to 100. For example: [30, 40, 30, 20]")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Temporal Pattern"
        verbose_name_plural = "Temporal Patterns"
