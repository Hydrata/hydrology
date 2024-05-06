import copy
import pytz
import math
import matplotlib.pyplot as plt

from django.contrib.gis.db.models import PointField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.indexes import GinIndex
from datetime import datetime
from django.core.files import File
from io import BytesIO

from gn_anuga.models import Project

User = get_user_model()


class TimeSeries(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_created', verbose_name="Created by")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_owner', verbose_name="Owner")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=500)
    location_name = models.CharField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=500, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC', choices=[(tz, tz) for tz in pytz.all_timezones])
    data = JSONField(default=list(), blank=True, null=True)
    chart = models.ImageField(upload_to='timeseries/chart/', blank=True, null=True)

    def clean(self):
        required_keys = {'ts', 'value'}
        for data_index, data_point in enumerate(self.data):
            if not required_keys.issubset(data_point):
                raise ValidationError(f"The {required_keys} fields are required in each data point.")

            timestamp_string = data_point.get('ts')
            try:
                datetime.fromisoformat(timestamp_string.rstrip('Z'))
            except ValueError:
                raise ValidationError("All timestamps must be in ISO 8601 format.")

        if self.timezone not in pytz.all_timezones:
            raise ValidationError("The 'timezone' field must contain a valid timezone.")
        self.create_chart()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def data_with_datetimes(self):
        data_with_datetimes = []
        tz = pytz.timezone(self.timezone)
        for data_point in self.data:
            data_point_copy = data_point.copy()
            data_point_copy['ts'] = datetime.fromisoformat(data_point['ts'].rstrip('Z')).replace(tzinfo=tz)
            data_with_datetimes.append(data_point_copy)
        return data_with_datetimes

    def create_chart(self):
        filename = f'{self.name}.png'
        timestamps = [item['ts'] for item in self.data]
        values = [item['value'] for item in self.data]
        plt.bar(timestamps, values)
        plt.tight_layout()  # Adjust layout to prevent cut-off

        # Save it to a BytesIO object
        file_buffer = BytesIO()
        plt.savefig(file_buffer, format='png')
        file_buffer.seek(0)

        chart_image = File(file_buffer, name=filename)
        self.chart.save(filename, chart_image, save=False)

    class Meta:
        indexes = [
            GinIndex(fields=['data']),
            models.Index(fields=['timezone']),
        ]


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
    location_name = models.CharField(max_length=500)
    location_geom = PointField()
    source = models.CharField(max_length=500)
    notes = models.TextField(blank=True, null=True)
    durations_in_mins = JSONField("Durations in Minutes", blank=True, null=True)
    ey_12 = JSONField("12EY", blank=True, null=True)
    ey_6 = JSONField("6EY", blank=True, null=True)  # 0.17yr ARI
    ey_4 = JSONField("4EY", blank=True, null=True)  # 0.25yr ARI
    ey_3 = JSONField("3EY", blank=True, null=True)  # 0.33yr ARI
    ey_2 = JSONField("2EY", blank=True, null=True)  # 0.5yr ARI
    ey_1 = JSONField("1EY", blank=True, null=True)  # 1yr ARI
    percent_50 = JSONField("50%", blank=True, null=True)  # 1.44yr ARI
    ey_0_5 = JSONField("0.5EY", blank=True, null=True)  # 2yr ARI
    percent_20 = JSONField("20%", blank=True, null=True)  # 4.48 yr ARI
    ey_0_2 = JSONField("0.2EY", blank=True, null=True)  # 5yr ARI
    percent_10 = JSONField("10%", blank=True, null=True)  # 10yr ARI
    percent_5 = JSONField("5%", blank=True, null=True)  # 20yr ARI
    percent_4 = JSONField("4%", blank=True, null=True)  # 25yr ARI
    percent_2 = JSONField("2%", blank=True, null=True)  # 50yr ARI
    percent_1 = JSONField("1%", blank=True, null=True)  # 100yr ARI
    percent_0_5 = JSONField("0.5%", blank=True, null=True)  # 200yr ARI
    percent_0_2 = JSONField("0.2%", blank=True, null=True)  # 500yr ARI
    percent_0_01 = JSONField("0.01%", blank=True, null=True)  # 1000yr ARI
    percent_0_05 = JSONField("0.05%", blank=True, null=True)  # 2000yr ARI
    percent_0_002 = JSONField("0.02%", blank=True, null=True)  # 5000yr ARI,
    original_units = models.CharField(max_length=4, choices=UNIT_CHOICES, default='mm',)
    saved_units = models.CharField(max_length=4, choices=UNIT_CHOICES, default='mm',)
    conversion_complete = models.BooleanField(default=False)
    chart = models.ImageField(upload_to='idftable/chart/', blank=True, null=True)
    selected_durations = JSONField("Selected Durations", blank=True, null=True)
    selected_frequencies = JSONField("Selected Frequencies", blank=True, null=True)

    def convert_to_mm(self, value):
        conversion_factor = self.UNIT_CONVERSIONS[self.original_units]
        return value * conversion_factor
    
    @property
    def frequency_field_labels(self):
        return [
            'ey_12',
            'ey_6',
            'ey_4',
            'ey_3',
            'ey_2',
            'ey_1',
            'percent_50',
            'ey_0_5',
            'percent_20',
            'ey_0_2',
            'percent_10',
            'percent_5',
            'percent_4',
            'percent_2',
            'percent_1',
            'percent_0_5',
            'percent_0_2',
            'percent_0_01',
            'percent_0_05',
            'percent_0_002',
        ]

    @property
    def frequencies(self):
        frequencies = dict()
        for field_label in self.frequency_field_labels:
            frequencies.update({field_label: getattr(self, field_label)})
        return frequencies

    @property
    def frequencies_filtered(self):
        frequencies_filtered = copy.deepcopy(self.frequencies)
        for label, frequency in self.frequencies.items():
            if frequency is not None:
                if not isinstance(frequency, list):
                    raise ValidationError(f"JSON field {label} does not contain a list.")
            else:
                del frequencies_filtered[label]
        return frequencies_filtered

    def clean(self):
        duration_lengths = list()
        for label, frequency in self.frequencies_filtered.items():
            duration_lengths.append(len(frequency))

        if len(set(duration_lengths)) > 1:
            raise ValidationError("All durations must be lists of the same length.")

        # convert units if necessary
        if self.original_units != self.MM and not self.conversion_complete:
            for label, frequency in self.frequencies_filtered.items():
                converted_frequency = [self.convert_to_mm(value) for value in frequency]
                setattr(self, label, converted_frequency)
            self.conversion_complete = True

        if self.selected_durations:
            if isinstance(self.selected_durations, list):
                for duration in self.selected_durations:
                    if duration not in self.durations_in_mins:
                        raise ValidationError('Selected duration is not in available durations')
            else:
                raise ValidationError('Selected durations must be a list of integers')

        if self.selected_frequencies:
            if isinstance(self.selected_durations, list):
                for frequency in self.selected_frequencies:
                    if frequency not in self.frequencies_filtered:
                        raise ValidationError('Selected frequency is not in available frequencies')
            else:
                raise ValidationError('Selected frequencies must be a list of strings')

    def save(self, *args, **kwargs):
        self.full_clean()
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
        depths = self.frequencies_filtered[frequency]
        duration_index = self.durations_in_mins.index(duration_in_minutes)
        total_depth_value = depths[duration_index]
        timeseries_data = list()
        timestep_in_seconds = 60 * (duration_in_minutes / len(temporal_pattern.pattern))

        for index, relative_proportion in enumerate(temporal_pattern.pattern):
            current_timestamp_python = datetime.fromtimestamp(index * timestep_in_seconds, pytz.UTC)
            current_timestamp_iso8601 = current_timestamp_python.isoformat()
            timeseries_data.append({
                'ts': current_timestamp_iso8601,
                'value': total_depth_value * relative_proportion
            })

        # Add the final timestamp to ensure we have a timeseries the same duration as duration_in_minutes
        final_index = len(temporal_pattern.pattern)
        current_timestamp_python = datetime.fromtimestamp(final_index * timestep_in_seconds, pytz.UTC)
        current_timestamp_iso8601 = current_timestamp_python.isoformat()
        timeseries_data.append({
            'ts': current_timestamp_iso8601,
            'value': total_depth_value * temporal_pattern.pattern[-1]
        })

        timeseries = TimeSeries.objects.create(
            name=f"{self.location_name} - {frequency} - {duration_in_minutes} minutes",
            data=timeseries_data,
            created_by=user
        )
        return timeseries



    def __str__(self):
        return self.location_name

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
    source = models.CharField(max_length=500)
    notes = models.TextField(blank=True, null=True)
    pattern = JSONField("Pattern", blank=True, null=True)

    def clean(self):
        if not sum(self.pattern) == 1:
            raise ValidationError("The temporal pattern must sum to 1. For example: [0.3, 0.4, 0.3, 0.2]")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Temporal Pattern"
        verbose_name_plural = "Temporal Patterns"
