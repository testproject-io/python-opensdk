# Copyright 2020 TestProject (https://testproject.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import os
from typing import Union

from src.testproject.enums import EnvironmentVariable
from src.testproject.sdk.drivers.webdriver import Remote
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


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
            driver: Union[Remote, BaseDriver] = kwargs.get('driver')
            if project:
                os.environ[EnvironmentVariable.TP_PROJECT_NAME.value] = project
            if job:
                os.environ[EnvironmentVariable.TP_JOB_NAME.value] = job
            if test:
                os.environ[EnvironmentVariable.TP_TEST_NAME.value] = test
                if driver:
                    driver.command_executor.test_name = test
            return func(*args, **kwargs)

        return wrapper

    return report_decorator
