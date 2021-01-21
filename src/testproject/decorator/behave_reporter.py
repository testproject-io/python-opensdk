# Copyright 2021 TestProject (https://testproject.io)
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

from src.testproject.helpers.activesessionhelper import get_active_driver_instance

from functools import wraps
from src.testproject.enums import EnvironmentVariable
import os


def behave_reporter(func=None, *, screenshot: bool = False):
    """Enables automatic logging of Gherkin syntax, including a screenshot when screenshot argument is True, by default
    screenshots are taken only when a step fails.
    Args:
            func: Original function wrapped by the annotation.
            screenshot (bool): True if a screenshot should be taken for each step, otherwise (False) only on failure.
    """
    def _behave_reporter(_func):
        @wraps(_func)
        def wrapper(*args, **kwargs):
            # Disable automatic test and command reporting.
            if os.getenv("TP_DISABLE_AUTO_REPORTING") != "True":
                os.environ[EnvironmentVariable.TP_DISABLE_AUTO_REPORTING.value] = "True"
            # Report step or test based on the constant hook name.
            # Behave always calls the methods with the arguments in the following order: (context, step/scenario).
            hook_name = _func.__name__
            if hook_name == "after_step":
                driver = get_active_driver_instance()
                step = args[1]
                report_step(driver=driver, step=step, screenshot=screenshot)
            if hook_name == "after_scenario":
                driver = get_active_driver_instance()
                scenario = args[1]
                report_test(driver=driver, scenario=scenario)
            return _func(*args, **kwargs)
        return wrapper

    if func:
        return _behave_reporter(func)

    return _behave_reporter


def report_step(driver, step, screenshot):
    """Report behave step """
    step_description = "{} {}".format(step.keyword, step.name)
    step_status = True if step.status == 'passed' else False
    step_message = "{} {}".format(type(step.exception).__name__, str(step.exception)) if not step_status \
        else step_description
    driver.report().step(description=step_description, message=step_message, passed=step_status, screenshot=screenshot)


def report_test(driver, scenario):
    """Report behave scenario """
    test_name = scenario.name
    test_status = True if scenario.status == 'passed' else False
    driver.report().test(name=test_name, passed=test_status)
