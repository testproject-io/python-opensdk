import functools
import os

from src.testproject.enums import EnvironmentVariable


def report(project: str = None, job: str = None, test: str = None):
    """Enables setting a custom name for the project, job and test for reporting purposes
        Args:
            project (str): The name of the project
            job (str): The name of the job
            test (str): The name of the test
        Returns:
            report_decorator: The decorated test method.
    """

    def report_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if project is not None:
                os.environ[EnvironmentVariable.TP_PROJECT_NAME.value] = project
            if job is not None:
                os.environ[EnvironmentVariable.TP_JOB_NAME.value] = job
            if test is not None:
                os.environ[EnvironmentVariable.TP_TEST_NAME.value] = test
            return func(*args, **kwargs)

        return wrapper

    return report_decorator
