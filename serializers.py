from django.contrib.auth import get_user_model
from rest_framework import serializers
from hydrology.models import IDFTable, TemporalPattern, TimeSeries

import logging
logger = logging.getLogger(__name__)
User = get_user_model()


class IDFTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = IDFTable
        fields = '__all__'


class TemporalPatternSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemporalPattern
        fields = '__all__'


class TimeSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeSeries
        fields = '__all__'
