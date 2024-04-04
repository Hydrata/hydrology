import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from hydrology.models import IDFTable

User = get_user_model()


@pytest.mark.django_db
class TestIDFTableModel:

    def setup_method(self):
        self.user = User.objects.create(username='test_user')
        self.valid_data = {
            'durations_in_mins': [5, 10, 15, 30, 60, 2*60, 3*60, 6*60, 12*60, 24*60, 2*24*60, 3*24*60, 4*24*60, 7*24*60, 10*24*60, 20*24*60, 30*24*60, 45*24*60, 60*24*60],
            'ey_12': None,
            'ey_6': None,
            'ey_4': None,
            'ey_3': None,
            'ey_2': None,
            'ey_1': [0.407, 0.632, 0.775, 1.02, 1.25, 1.49, 1.59, 1.88, 2.19, 2.57, 2.99, 3.2, 3.41, 3.99, 4.56, 6.24, 7.65, 9.58, 11.3],
            'percent_50': None,
            'ey_0_5': [0.483, 0.753, 0.921, 1.23, 1.51, 1.8, 1.92, 2.26, 2.63, 3.07, 3.56, 3.8, 4.05, 4.72, 5.38, 7.33, 8.96, 11.2, 13.3],
            'percent_20': [0.573, 0.89, 1.09, 1.5, 1.88, 2.22, 2.38, 2.78, 3.22, 3.73, 4.3, 4.57, 4.85, 5.54, 6.3, 8.45, 10.2, 12.7, 15],
            'ey_0_2': None,
            'percent_10': [0.645, 0.995, 1.22, 1.7, 2.16, 2.57, 2.75, 3.23, 3.72, 4.31, 4.93, 5.22, 5.52, 6.23, 7.04, 9.34, 11.3, 13.9, 16.4],
            'percent_5': None,
            'percent_4': [0.737, 1.13, 1.39, 1.96, 2.55, 3.07, 3.31, 3.88, 4.45, 5.17, 5.88, 6.19, 6.49, 7.22, 8.11, 10.6, 12.7, 15.6, 18.3],
            'percent_2': [0.809, 1.23, 1.52, 2.17, 2.86, 3.49, 3.79, 4.44, 5.07, 5.95, 6.73, 7.03, 7.34, 8.07, 8.99, 11.6, 14, 16.9, 19.8],
            'percent_1': [0.88, 1.32, 1.65, 2.38, 3.18, 3.96, 4.32, 5.07, 5.76, 6.83, 7.69, 7.98, 8.27, 8.98, 9.95, 12.7, 15.2, 18.3, 21.4],
            'percent_0_5': [0.955, 1.42, 1.77, 2.59, 3.51, 4.48, 4.92, 5.76, 6.53, 7.84, 8.79, 9.06, 9.32, 9.99, 11, 13.8, 16.6, 19.8, 23.1],
            'percent_0_2': [1.06, 1.55, 1.94, 2.87, 3.97, 5.26, 5.82, 6.83, 7.68, 9.43, 10.5, 10.7, 10.9, 11.5, 12.5, 15.4, 18.6, 21.9, 25.4],
            'percent_0_01': [1.13, 1.65, 2.06, 3.08, 4.33, 5.93, 6.62, 7.76, 8.69, 10.9, 12, 12.2, 12.4, 12.8, 13.8, 16.7, 20.2, 23.5, 27.2],
            'percent_0_05': None,
            'percent_0_002': None,
        }
        self.latitude = 40.0308
        self.longitude = -88.5889

    def test_valid_jsonfields_same_length(self):
        idf_table = IDFTable(
            created_by=self.user,
            location_name='Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Test Source',
            notes='Test note',
            **self.valid_data
        )
        idf_table.save()

    def test_invalid_jsonfields_different_lengths_raises_error(self):
        # Alter one of the lists to make it a different length
        invalid_data = self.valid_data.copy()
        invalid_data['ey_6'] = [1, 2, 3]

        idf_table = IDFTable(
            created_by=self.user,
            location_name='Invalid Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Invalid Test Source',
            notes='Invalid test note',
            **invalid_data
        )

        with pytest.raises(ValidationError):
            idf_table.save()

    def test_invalid_jsonfields_not_list_raises_error(self):
        invalid_data = self.valid_data.copy()
        invalid_data['ey_12'] = "not a list"

        idf_table = IDFTable(
            created_by=self.user,
            location_name='Another Invalid Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Another Invalid Test Source',
            notes='Another invalid test note',
            **invalid_data
        )
        with pytest.raises(ValidationError):
            idf_table.save()

    @pytest.mark.parametrize("aep, expected_ari", [
        (62.3, 1),
        (50, 1.44),
        (10, 10),
        (1, 100),
        (0.1, 1000),
    ])
    def test_ari_from_aep(self, aep, expected_ari):
        assert pytest.approx(IDFTable.ari_from_aep(aep), 0.1) == expected_ari

    @pytest.mark.parametrize("ari, expected_aep", [
        (1, 62.3),
        (2, 40),
        (10, 10),
        (25, 4),
        (100, 1),
        (1000, 0.1)
    ])
    def test_aep_from_ari(self, ari, expected_aep):
        assert pytest.approx(IDFTable.aep_from_ari(ari), 0.1) == expected_aep
