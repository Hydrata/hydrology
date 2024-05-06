from hydrology.serializers import IDFTableSerializer, TimeSeriesSerializer, TemporalPatternSerializer

import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from gn_anuga.models import Project

logger = logging.getLogger(__name__)


class IDFTableViewSet(viewsets.ModelViewSet):
    serializer_class = IDFTableSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)

    def get_queryset(self):
        project_id = int(self.kwargs['project_id'])
        project = Project.objects.get(id=project_id)
        idf_tables = project.idf_tables.all()
        return idf_tables


class TimeSeriesViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSeriesSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)

    def get_queryset(self):
        project_id = int(self.kwargs['project_id'])
        project = Project.objects.get(id=project_id)
        time_series = project.time_series.all()
        return time_series


class TemporalPatternViewSet(viewsets.ModelViewSet):
    serializer_class = TemporalPatternSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, owner=self.request.user)

    def get_queryset(self):
        project_id = int(self.kwargs['project_id'])
        project = Project.objects.get(id=project_id)
        temporal_patterns = project.temporal_patterns.all()
        return temporal_patterns
