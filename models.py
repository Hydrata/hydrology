from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.indexes import GinIndex
from datetime import datetime
import pytz
import csv


class TimeSeries(models.Model):
    pass
