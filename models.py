from django.contrib.gis.db.models import PointField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.indexes import GinIndex
from datetime import datetime
import pytz
import math
User = get_user_model()


class TimeSeries(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_created', verbose_name="Created by")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='timeseries_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    data = JSONField()
    timezone = models.CharField(max_length=50, default='UTC', choices=[(tz, tz) for tz in pytz.all_timezones])

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

    class Meta:
        indexes = [
            GinIndex(fields=['data']),
            models.Index(fields=['timezone']),
        ]


class IDFTable(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='idf_table_created', verbose_name="Created by")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='idf_table_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
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
    percent_0_002 = JSONField("0.02%", blank=True, null=True)  # 5000yr ARI

    def clean(self):
        recurrance_intervals = [
            self.ey_12,
            self.ey_6,
            self.ey_4,
            self.ey_3,
            self.ey_2,
            self.ey_1,
            self.percent_50,
            self.ey_0_5,
            self.percent_20,
            self.ey_0_2,
            self.percent_10,
            self.percent_5,
            self.percent_4,
            self.percent_2,
            self.percent_1,
            self.percent_0_5,
            self.percent_0_2,
            self.percent_0_01,
            self.percent_0_05,
            self.percent_0_002,
        ]
        recurrance_intervals_filtered = list()
        duration_lengths = list()
        for recurrance_interval in recurrance_intervals:
            if recurrance_interval is not None:
                if not isinstance(recurrance_interval, list):
                    raise ValidationError(f"JSON field {recurrance_interval} is not a list.")
                recurrance_intervals_filtered.append(recurrance_interval)
                duration_lengths.append(len(recurrance_interval))

        if len(set(duration_lengths)) > 1:
            raise ValidationError("All durations must be lists of the same length.")

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

    def __str__(self):
        return self.location_name

    class Meta:
        verbose_name = "IDF Table"
        verbose_name_plural = "IDF Tables"


class TemporalPattern(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temporal_pattern_created', verbose_name="Created by")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='temporal_pattern_updated', verbose_name="Updated by")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
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
