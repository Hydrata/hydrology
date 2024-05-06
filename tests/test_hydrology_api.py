import pytest

from gn_anuga.models import Project
from hydrology.models import IDFTable, TemporalPattern, TimeSeries


@pytest.mark.django_db
class TestIDFTableViewSet:
    def test_list_idf_tables(self, api_client_with_project, create_idf_table):
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/idf-table/')
        assert response.status_code == 200
        assert len(response.data) == 1  # Assuming this is the only object in the database

    def test_create_idftable(self, api_client_with_project, create_idf_table):
        project = Project.objects.latest('id')
        response = api_client_with_project.post(f'/anuga/api/{project.id}/idf-table/', {
            'location_name': 'New Location',
            'location_geom': {
                "type": "Point",
                "coordinates": [
                    -105.01621,
                    39.57422
                ]
            },
            'source': 'Test Data'
        }, format='json')
        assert response.status_code == 201
        assert IDFTable.objects.count() == 2  # Assuming one was already created in setup

    def test_retrieve_idftable(self, api_client_with_project, create_idf_table):
        idf_table = create_idf_table
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/idf-table/{idf_table.id}/')
        assert response.status_code == 200
        assert response.data['location_name'] == 'Test Location'

    def test_update_idftable(self, api_client_with_project, create_idf_table):
        idf_table = create_idf_table
        project = Project.objects.latest('id')
        response = api_client_with_project.patch(f'/anuga/api/{project.id}/idf-table/{idf_table.pk}/', {
            'location_name': 'Updated Location',
        }, format='json')
        assert response.status_code == 200
        updated_idf_table = IDFTable.objects.get(pk=idf_table.pk)
        assert updated_idf_table.location_name == 'Updated Location'

    def test_delete_idftable(self, api_client_with_project, create_idf_table):
        idf_table = create_idf_table
        project = Project.objects.latest('id')
        response = api_client_with_project.delete(f'/anuga/api/{project.id}/idf-table/{idf_table.pk}/')
        assert response.status_code == 204
        assert IDFTable.objects.count() == 0


@pytest.mark.django_db
class TestTemporalPatternViewSet:
    def test_list_temporal_patterns(self, api_client_with_project, create_temporal_pattern):
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/temporal-pattern/')
        assert response.status_code == 200
        assert len(response.data) == 1  # Assuming this is the only object in the database

    def test_create_temporal_pattern(self, api_client_with_project, create_temporal_pattern):
        project = Project.objects.latest('id')
        response = api_client_with_project.post(f'/anuga/api/{project.id}/temporal-pattern/', {
            'name': "Valid Test Pattern",
            'pattern': [0.1, 0.2, 0.45, 0.25],
            'source': "Test Source"
        }, format='json')
        assert response.status_code == 201
        assert TemporalPattern.objects.count() == 2  # Assuming one was already created in setup

    def test_retrieve_temporal_pattern(self, api_client_with_project, create_temporal_pattern):
        temporal_pattern = create_temporal_pattern
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/temporal-pattern/{temporal_pattern.id}/')
        assert response.status_code == 200
        assert response.data['name'] == "Valid Test Pattern"

    def test_update_temporal_pattern(self, api_client_with_project, create_temporal_pattern):
        temporal_pattern = create_temporal_pattern
        project = Project.objects.latest('id')
        response = api_client_with_project.patch(f'/anuga/api/{project.id}/temporal-pattern/{temporal_pattern.pk}/', {
            'name': 'Updated Valid Test Pattern',
        }, format='json')
        assert response.status_code == 200
        updated_temporal_pattern = TemporalPattern.objects.get(pk=temporal_pattern.pk)
        assert updated_temporal_pattern.name == 'Updated Valid Test Pattern'

    def test_delete_temporal_pattern(self, api_client_with_project, create_temporal_pattern):
        temporal_pattern = create_temporal_pattern
        project = Project.objects.latest('id')
        response = api_client_with_project.delete(f'/anuga/api/{project.id}/temporal-pattern/{temporal_pattern.pk}/')
        assert response.status_code == 204
        assert TemporalPattern.objects.count() == 0


@pytest.mark.django_db
class TestTimeSereiesViewSet:
    def test_list_time_series(self, api_client_with_project, create_time_series):
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/time-series/')
        assert response.status_code == 200
        assert len(response.data) == 1  # Assuming this is the only object in the database

    def test_create_time_series(self, api_client_with_project, create_time_series):
        project = Project.objects.latest('id')
        response = api_client_with_project.post(f'/anuga/api/{project.id}/time-series/', {
            'data': [
                {'ts': '2022-06-01T00:00:00', 'value': 10},
                {'ts': '2022-07-01T00:00:00', 'value': 20},
                {'ts': '2022-08-01T00:00:00', 'value': 30}
            ],
            'name': 'Test Data',
            'source': 'Test Data'
        }, format='json')
        assert response.status_code == 201
        assert TimeSeries.objects.count() == 2  # Assuming one was already created in setup

    def test_retrieve_time_series(self, api_client_with_project, create_time_series):
        time_series = create_time_series
        project = Project.objects.latest('id')
        response = api_client_with_project.get(f'/anuga/api/{project.id}/time-series/{time_series.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Valid Time Series'

    def test_update_time_series(self, api_client_with_project, create_time_series):
        updated_data = [
                {'ts': '2022-06-01T00:00:00', 'value': 20},
                {'ts': '2022-07-01T00:00:00', 'value': 40},
                {'ts': '2022-08-01T00:00:00', 'value': 60}
            ]
        time_series = create_time_series
        project = Project.objects.latest('id')
        response = api_client_with_project.patch(f'/anuga/api/{project.id}/time-series/{time_series.pk}/', {
            'name': 'Updated Name',
            'data': updated_data
        }, format='json')
        assert response.status_code == 200
        updated_time_series = TimeSeries.objects.get(pk=time_series.pk)
        assert updated_time_series.name == 'Updated Name'
        assert updated_time_series.data == updated_data

    def test_delete_time_series(self, api_client_with_project, create_time_series):
        time_series = create_time_series
        project = Project.objects.latest('id')
        response = api_client_with_project.delete(f'/anuga/api/{project.id}/time-series/{time_series.pk}/')
        assert response.status_code == 204
        assert TimeSeries.objects.count() == 0
