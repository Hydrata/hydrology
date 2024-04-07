from django.db import models


class DummyProject(models.Model):

    class Meta:
        app_label = 'hydrology'
        managed = False
