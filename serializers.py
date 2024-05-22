from django.contrib.auth import get_user_model
from rest_framework import serializers
from hydrology.models import IDFTable, TemporalPattern, TimeSeries

import logging
logger = logging.getLogger(__name__)
User = get_user_model()


from rest_framework.serializers import SerializerMethodField


class IDFTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = IDFTable
        widgets = {
            'name': 'text',
            'source': 'text',
            'notes': 'textarea',
            'durations_in_mins': 'list-of-numbers',
            'original_units': 'textarea',
            'saved_units': 'textarea',
            'chart': 'image',
            'selected_durations': 'list-of-numbers',
            'selected_frequencies': 'list-of-numbers'
        }
        fields = [
            'id'
            ] + list(widgets.keys()) + IDFTable.FREQUENCY_FIELD_LABELS

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['widgets'] = self.Meta.widgets
        return representation


class TemporalPatternSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemporalPattern
        fields = '__all__'


class TimeSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeSeries
        fields = '__all__'
