import boto3
import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.conf import settings
from rest_framework.test import APIClient
from gn_anuga.models import Project
from hydrology.models import IDFTable, TemporalPattern, TimeSeries

User = get_user_model()

@pytest.fixture
def s3():
    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = boto3.client('s3')
    # paginator = s3.get_paginator('list_objects_v2')
    # for page in paginator.paginate(Bucket='anuga-test-storage'):
    #     if 'Contents' in page:
    #         objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
    #         s3.delete_objects(Bucket='anuga-test-storage', Delete={'Objects': objects_to_delete})
    return s3

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
        data = [
            {'ts': '2022-06-01T00:00:00Z+00:00', 'value': 10},
            {'ts': '2022-07-01T00:00:00Z+00:00', 'value': 20},
            {'ts': '2022-08-01T00:00:00Z+00:00', 'value': 30}
        ],
        source="Test Source",
        project=project
    )
    return time_series
