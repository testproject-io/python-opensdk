import os
import pytest

from src.testproject.decorator import report
from src.testproject.enums import EnvironmentVariable


@pytest.fixture
def clear_env_vars():
    yield
    for env_var in [
        EnvironmentVariable.TP_PROJECT_NAME,
        EnvironmentVariable.TP_JOB_NAME,
        EnvironmentVariable.TP_TEST_NAME,
    ]:
        try:
            os.environ.pop(env_var.value)
        except KeyError:
            pass


@report(project="My project", job="My job", test="My test")
def test_decorator_sets_environment_variables(clear_env_vars):
    assert os.environ.get(EnvironmentVariable.TP_PROJECT_NAME.value) == "My project"
    assert os.environ.get(EnvironmentVariable.TP_JOB_NAME.value) == "My job"
    assert os.environ.get(EnvironmentVariable.TP_TEST_NAME.value) == "My test"


@report(test="Another test")
def test_environment_variables_can_be_removed(clear_env_vars):
    assert os.environ.get(EnvironmentVariable.TP_TEST_NAME.value) == "Another test"
    EnvironmentVariable.remove(EnvironmentVariable.TP_TEST_NAME)
    assert os.environ.get(EnvironmentVariable.TP_TEST_NAME.value) is None
