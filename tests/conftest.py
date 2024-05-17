import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient
from gn_anuga.models import Project
from hydrology.models import IDFTable, TemporalPattern, TimeSeries

User = get_user_model()


@pytest.fixture
def create_user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def create_simple_project(create_user):
    user = create_user
    return Project.objects.create(
        name='Test Project',
        owner=user,
        created_by=user
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_with_project(create_simple_project):
    project = create_simple_project
    api = APIClient()
    api.force_authenticate(user=project.owner)
    return api


@pytest.fixture
def create_idf_table(create_user, create_simple_project):
    project = create_simple_project
    idf_table = IDFTable.objects.create(
        created_by=create_user,
        location_name="Test Location",
        location_geom=Point(30, 150),
        source="Test Source",
        project=project
    )
    return idf_table


@pytest.fixture
def create_temporal_pattern(create_user, create_simple_project):
    project = create_simple_project
    temporal_pattern = TemporalPattern.objects.create(
        created_by=create_user,
        name="Valid Test Pattern",
        pattern=[0.1, 0.2, 0.45, 0.25],
        source="Test Source",
        project=project
    )
    return temporal_pattern


@pytest.fixture
def create_time_series(create_user, create_simple_project):
    project = create_simple_project
    time_series = TimeSeries.objects.create(
        name='Valid Time Series',
        created_by=create_user,
        location_name="Test Location",
        source="Test Source",
        project=project
    )
    data = [
        {'ts': '2022-06-01T00:00:00Z+00:00', 'value': 10},
        {'ts': '2022-07-01T00:00:00Z+00:00', 'value': 20},
        {'ts': '2022-08-01T00:00:00Z+00:00', 'value': 30}
    ]
    time_series.import_stac_from_simple_array(data)
    return time_series
