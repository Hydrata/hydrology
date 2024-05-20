import datetime
import pytest
import pytz
import tempfile

from PIL import Image
from django.core.exceptions import ValidationError
from django.conf import settings
from hydrology.models import TimeSeries


@pytest.mark.django_db
class TestTimeSeriesModel:

    def setup_method(self):

        self.valid_time_data = [
            {'ts': '2022-06-01T00:00:00Z+00:00', 'value': 10},
            {'ts': '2022-07-01T00:00:00Z+00:00', 'value': 20},
            {'ts': '2022-08-01T00:00:00Z+00:00', 'value': 30}
        ]
        self.invalid_time_data = [
            {'ts': 'not a timestamp', 'value': 10},
            {'ts': '2022-07-01T00:00:00Z+00:00', 'value': 20},
            {'ts': '2022-08-01T00:00:00Z+00:00', 'value': 30}
        ]

    def test_time_series_creation_with_valid_data(self, s3):
        time_series = TimeSeries.objects.create(
            name='valid TimeSeries Name',
            timezone='UTC',
            data=self.valid_time_data
        )
        assert time_series.data
        with tempfile.NamedTemporaryFile() as chart_file:
            s3.download_file(settings.ANUGA_S3_DATA_BUCKET_NAME, f"{time_series.chart}", chart_file.name)
            with Image.open(chart_file.name) as img:
                width, height = img.size
                assert width > 10
                assert height > 10

    def test_time_series_creation_with_invalid_timestamps(self):
        with pytest.raises(ValidationError):
            time_series = TimeSeries.objects.create(
                name='valid TimeSeries Name',
                data=self.invalid_time_data,
                timezone='UTC'
            )

    def test_time_series_creation_with_invalid_timezone(self):
        with pytest.raises(ValidationError):
            time_series = TimeSeries.objects.create(
                name='valid TimeSeries Name',
                data=self.valid_time_data,
                timezone='InvalidTimezone'
            )

    def test_time_series_data_with_datetimes(self):
        time_series = TimeSeries.objects.create(
            name='valid TimeSeries Name',
            data=self.valid_time_data,
            timezone='UTC'
        )
        expected_data = [
            {'ts': datetime.datetime(2022, 6, 1, 0, 0, tzinfo=pytz.UTC), 'value': 10},
            {'ts': datetime.datetime(2022, 7, 1, 0, 0, tzinfo=pytz.UTC), 'value': 20},
            {'ts': datetime.datetime(2022, 8, 1, 0, 0, tzinfo=pytz.UTC), 'value': 30}
        ]
        assert time_series.data_with_datetimes == expected_data
