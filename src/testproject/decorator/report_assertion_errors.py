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
import sys
import traceback

from src.testproject.sdk.exceptions import SdkException

from src.testproject.sdk.drivers.webdriver import Remote, Generic

from src.testproject.sdk.drivers.webdriver.base import BaseDriver


def report_assertion_errors(func):
    """Enables automatic logging of failed assertions, including a screenshot"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as ae:
            _, _, tb = sys.exc_info()
            tb_info = traceback.extract_tb(tb)

            # Depending on the unit testing framework in use we need a different line in the stack
            line_index = -1 if os.getenv("PYTEST_CURRENT_TEST") is not None else -2

            # Depending on the unit testing framework we format the reported error differently
            description = (
                ae.__repr__()
                if os.getenv("PYTEST_CURRENT_TEST") is not None
                else str(ae)
            )

            _, line, function, text = tb_info[line_index]
            driver = __get_active_driver_instance()
            driver.report().step(
                description=description,
                message=f"Assertion failed on line {line} in {function}",
                passed=False,
                screenshot=False,
            )
            # raise the AssertionError again to make the test execution fail as intended
            raise ae

    return wrapper


def __get_active_driver_instance():
    """Get the current driver instance in use (BaseDriver, Remote or Generic) """
    driver = BaseDriver.instance()
    if driver is None:
        driver = Remote.instance()
        if driver is None:
            driver = Generic.instance()
            if driver is None:
                raise SdkException(
                    "No active driver instance found, so cannot report failed assertion"
                )

    return driver
