import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from hydrology.models import TemporalPattern

User = get_user_model()


@pytest.mark.django_db
class TestTemporalPattern:

    def setup_method(self):
        self.valid_pattern = [0.5, 0.5]
        self.user = User.objects.create(username='test_user')
        self.temporal_pattern = TemporalPattern.objects.create(
            pattern=self.valid_pattern,
            name="TestPattern",
            source="Imaginary test data"
        )

    def test_save_model(self):
        assert self.temporal_pattern.name == "TestPattern"
        assert self.temporal_pattern.pattern == self.valid_pattern

    def test_save_invalid_model_not_sum_one(self):
        test_pattern = [0.3, 0.5]
        self.temporal_pattern.pattern = test_pattern

        with pytest.raises(ValidationError):
            self.temporal_pattern.save()

    def test_save_invalid_pattern_not_floats(self):
        test_pattern = ["a string", 0.5]
        self.temporal_pattern.pattern = test_pattern

        with pytest.raises(TypeError):
            self.temporal_pattern.save()
