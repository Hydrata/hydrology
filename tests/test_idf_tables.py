import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from hydrology.models import IDFTable, TemporalPattern

User = get_user_model()


@pytest.mark.django_db
class TestIDFTableModel:

    def setup_method(self):
        self.user = User.objects.create(username='test_user')
        self.valid_data_inches = {
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
            'original_units': 'in'
        }
        self.valid_data_mm = {
            'durations_in_mins': [5, 10, 15, 30, 60, 2*60, 3*60, 6*60, 12*60, 24*60, 2*24*60, 3*24*60, 4*24*60, 7*24*60, 10*24*60, 20*24*60, 30*24*60, 45*24*60, 60*24*60],
            "ey_12": None,
            "ey_6": None,
            "ey_4": None,
            "ey_3": None,
            "ey_2": None,
            "ey_1": [
                10.337799999999998,
                16.052799999999998,
                19.685,
                25.907999999999998,
                31.75,
                37.846,
                40.386,
                47.751999999999995,
                55.626,
                65.27799999999999,
                75.946,
                81.28,
                86.614,
                101.346,
                115.82399999999998,
                158.496,
                194.31,
                243.332,
                287.02,
            ],
            "percent_50": None,
            "ey_0_5": [
                12.268199999999998,
                19.1262,
                23.3934,
                31.241999999999997,
                38.354,
                45.72,
                48.767999999999994,
                57.40399999999999,
                66.80199999999999,
                77.978,
                90.42399999999999,
                96.52,
                102.86999999999999,
                119.88799999999999,
                136.652,
                186.182,
                227.584,
                284.47999999999996,
                337.82,
            ],
            "percent_20": [
                14.554199999999998,
                22.605999999999998,
                27.686,
                38.099999999999994,
                47.751999999999995,
                56.388000000000005,
                60.45199999999999,
                70.612,
                81.788,
                94.74199999999999,
                109.21999999999998,
                116.078,
                123.18999999999998,
                140.71599999999998,
                160.01999999999998,
                214.62999999999997,
                259.08,
                322.58,
                381.0,
            ],
            "ey_0_2": None,
            "percent_10": [
                16.383,
                25.273,
                30.987999999999996,
                43.18,
                54.864,
                65.27799999999999,
                69.85,
                82.042,
                94.488,
                109.47399999999999,
                125.22199999999998,
                132.588,
                140.20799999999997,
                158.242,
                178.816,
                237.236,
                287.02,
                353.06,
                416.55999999999995,
            ],
            "percent_5": None,
            "percent_4": [
                18.7198,
                28.701999999999995,
                35.306,
                49.784,
                64.77,
                77.978,
                84.074,
                98.55199999999999,
                113.03,
                131.31799999999998,
                149.35199999999998,
                157.226,
                164.846,
                183.38799999999998,
                205.99399999999997,
                269.23999999999995,
                322.58,
                396.23999999999995,
                464.82,
            ],
            "percent_2": [
                20.5486,
                31.241999999999997,
                38.608,
                55.117999999999995,
                72.64399999999999,
                88.646,
                96.26599999999999,
                112.77600000000001,
                128.778,
                151.13,
                170.942,
                178.56199999999998,
                186.43599999999998,
                204.978,
                228.346,
                294.64,
                355.59999999999997,
                429.25999999999993,
                502.92,
            ],
            "percent_1": [
                22.352,
                33.528,
                41.91,
                60.45199999999999,
                80.772,
                100.58399999999999,
                109.728,
                128.778,
                146.30399999999997,
                173.482,
                195.326,
                202.692,
                210.05799999999996,
                228.09199999999998,
                252.72999999999996,
                322.58,
                386.08,
                464.82,
                543.56,
            ],
            "percent_0_5": [
                24.256999999999998,
                36.068,
                44.958,
                65.78599999999999,
                89.154,
                113.792,
                124.96799999999999,
                146.30399999999997,
                165.862,
                199.136,
                223.26599999999996,
                230.124,
                236.72799999999998,
                253.74599999999998,
                279.4,
                350.52,
                421.64,
                502.92,
                586.74,
            ],
            "percent_0_2": [
                26.924,
                39.37,
                49.275999999999996,
                72.898,
                100.838,
                133.60399999999998,
                147.828,
                173.482,
                195.07199999999997,
                239.522,
                266.7,
                271.78,
                276.86,
                292.09999999999997,
                317.5,
                391.15999999999997,
                472.44,
                556.2599999999999,
                645.16,
            ],
            "percent_0_01": [
                28.701999999999995,
                41.91,
                52.324,
                78.232,
                109.982,
                150.62199999999999,
                168.148,
                197.10399999999998,
                220.72599999999997,
                276.86,
                304.79999999999995,
                309.87999999999994,
                314.96,
                325.12,
                350.52,
                424.17999999999995,
                513.0799999999999,
                596.9,
                690.88,
            ],
            "percent_0_05": None,
            "percent_0_002": None,
            'original_units': 'mm'
        }
        self.latitude = 40.0308
        self.longitude = -88.5889

    def test_valid_cumulative_data_in_inches(self):
        idf_table = IDFTable.objects.create(
            created_by=self.user,
            location_name='Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Test Source',
            notes='Test note',
            **self.valid_data_inches
        )
        for label, frequency in idf_table.frequencies.items():
            assert frequency == self.valid_data_mm.get(label)

    def test_valid_cumulative_data_in_millimeters(self):
        idf_table = IDFTable.objects.create(
            created_by=self.user,
            location_name='Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Test Source',
            notes='Test note',
            **self.valid_data_mm
        )
        for label, frequency in idf_table.frequencies.items():
            assert frequency == self.valid_data_mm.get(label)

    def test_invalid_jsonfields_different_lengths_raises_error(self):
        # Alter one of the lists to make it a different length
        invalid_data = self.valid_data_inches.copy()
        invalid_data['ey_6'] = [1, 2, 3]

        with pytest.raises(ValidationError):
            idf_table = IDFTable.objects.create(
                created_by=self.user,
                location_name='Invalid Test Location',
                location_geom=Point(self.longitude, self.latitude),
                source='Invalid Test Source',
                notes='Invalid test note',
                **invalid_data
            )

    def test_invalid_jsonfields_not_list_raises_error(self):
        invalid_data = self.valid_data_inches.copy()
        invalid_data['ey_12'] = "not a list"

        with pytest.raises(ValidationError):
            idf_table = IDFTable.objects.create(
                created_by=self.user,
                location_name='Another Invalid Test Location',
                location_geom=Point(self.longitude, self.latitude),
                source='Another Invalid Test Source',
                notes='Another invalid test note',
                **invalid_data
            )

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

    def test_create_timeseries_from_idftable(self):
        expected_timeseries = [
            {"ts": "1970-01-01T00:00:00+00:00", "value": 5.4864},
            {"ts": "1970-01-01T00:07:30+00:00", "value": 1.09728},
            {"ts": "1970-01-01T00:15:00+00:00", "value": 9.87552},
            {"ts": "1970-01-01T00:22:30+00:00", "value": 18.653760000000002},
            {"ts": "1970-01-01T00:30:00+00:00", "value": 6.0350399999999995},
            {"ts": "1970-01-01T00:37:30+00:00", "value": 2.7432},
            {"ts": "1970-01-01T00:45:00+00:00", "value": 6.583679999999999},
            {"ts": "1970-01-01T00:52:30+00:00", "value": 4.38912},
            {"ts": "1970-01-01T01:00:00+00:00", "value": 4.38912},
        ]

        idf_table = IDFTable.objects.create(
            created_by=self.user,
            location_name='Test Location',
            location_geom=Point(self.longitude, self.latitude),
            source='Test Source',
            notes='Test note',
            **self.valid_data_mm
        )
        duration = 60
        frequency = 'percent_10'
        temporal_pattern_list = [0.10, 0.02, 0.18, 0.34, 0.11, 0.05, 0.12, 0.08,]
        temporal_pattern = TemporalPattern.objects.create(
            pattern=temporal_pattern_list,
            name="TestPattern",
            source="Imaginary test data"
        )
        timeseries = idf_table.create_timeseries(duration, frequency, temporal_pattern, user=None)
        assert timeseries.data == expected_timeseries
        assert timeseries.chart.size >= 16949

    def test_selected_frequencies_and_durations(self):
        pass
