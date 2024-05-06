from django.urls import include, path
from rest_framework.routers import DefaultRouter
from hydrology import api

router = DefaultRouter()
router.register('<str:project_id>/temporal-pattern', api.TemporalPatternViewSet, basename='temporal-pattern')
router.register('<str:project_id>/idf-table', api.IDFTableViewSet, basename='idf-table')
router.register('<str:project_id>/time-series', api.TimeSeriesViewSet, basename='time-series')

urlpatterns = [
    path('anuga/api/', include(router.urls))
]