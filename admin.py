from django.contrib import admin
from hydrology.models import IDFTable, TemporalPattern, TimeSeries


class IDFTableAdmin(admin.ModelAdmin):
    list_filter = ('project',)
    list_display = [f.name for f in IDFTable._meta.fields]


class TemporalPatternAdmin(admin.ModelAdmin):
    list_filter = ('project',)
    list_display = [f.name for f in TemporalPattern._meta.fields]


class TimeSeriesAdmin(admin.ModelAdmin):
    list_filter = ('project',)
    list_display = [f.name for f in TimeSeries._meta.fields]


admin.site.register(IDFTable, IDFTableAdmin)
admin.site.register(TemporalPattern, TemporalPatternAdmin)
admin.site.register(TimeSeries, TimeSeriesAdmin)