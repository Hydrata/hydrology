from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.indexes import GinIndex
from datetime import datetime
import pytz


class TimeSeries(models.Model):
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
