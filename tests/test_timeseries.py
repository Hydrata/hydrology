import datetime
import pytest
import pytz

from django.core.exceptions import ValidationError
from hydrology.models import TimeSeries


@pytest.mark.django_db
class TestTimeSeriesModel:

    def setup_method(self):
        self.valid_time_data = [
            {'ts': '2022-06-01T00:00:00', 'value': 10},
            {'ts': '2022-07-01T00:00:00', 'value': 20},
            {'ts': '2022-08-01T00:00:00', 'value': 30}
        ]
        self.invalid_time_data = [
            {'ts': 'not a timestamp', 'value': 10},
            {'ts': '2022-07-01T00:00:00', 'value': 20},
            {'ts': '2022-08-01T00:00:00', 'value': 30}
        ]

    def test_model_creation_with_valid_data(self):
        time_series = TimeSeries.objects.create(data=self.valid_time_data, timezone='UTC')
        assert time_series is not None
        assert time_series.data == self.valid_time_data
        assert time_series.timezone == 'UTC'

    def test_model_with_invalid_timestamps(self):
        time_series = TimeSeries(data=self.invalid_time_data, timezone='UTC')
        with pytest.raises(ValidationError):
            time_series.save()

    def test_model_with_invalid_timezone(self):
        time_series = TimeSeries(data=self.valid_time_data, timezone='InvalidTimezone')
        with pytest.raises(ValidationError):
            time_series.save()

    def test_data_with_datetimes(self):
        time_series = TimeSeries.objects.create(data=self.valid_time_data, timezone='UTC')
        expected_data = [
            {'ts': datetime.datetime(2022, 6, 1, 0, 0, tzinfo=pytz.UTC), 'value': 10},
            {'ts': datetime.datetime(2022, 7, 1, 0, 0, tzinfo=pytz.UTC), 'value': 20},
            {'ts': datetime.datetime(2022, 8, 1, 0, 0, tzinfo=pytz.UTC), 'value': 30}
        ]
        assert time_series.data_with_datetimes == expected_data