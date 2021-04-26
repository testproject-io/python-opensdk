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
import os
from src.testproject.helpers.activesessionhelper import get_active_driver_instance
from src.testproject.enums import EnvironmentVariable
from decorator import decorator


@decorator
def pytestBDD_reporter(func, screenshot: bool = True, *args, **kwargs):
    """Enables automatic logging of Gherkin syntax, including  a screenshot when screenshot argument is True, by default
    screenshots are taken only when a step fails.
    Args:
            func: Original function decorated by the annotation.
            screenshot (bool): True if a screenshot should be taken for each step, otherwise (False) only on failure.
    """
    if os.getenv("TP_DISABLE_REPORTING") == "True":
        return pytestBDD_reporter

    os.environ[EnvironmentVariable.TP_DISABLE_AUTO_REPORTING.value] = "True"

    hook_name = func.__name__

    if hook_name == "pytest_bdd_after_step":
        driver = get_active_driver_instance()
        step = args[3]
        message = "{} {}".format(step.keyword, step.name)

        report_step(driver=driver, step=step, screenshot=screenshot, message=message)

    elif hook_name == "pytest_bdd_step_error":
        driver = get_active_driver_instance()
        step = args[3]
        exception = args[6]
        step.failed = True
        message = "{} {}".format(type(exception).__name__, str(exception))

        report_step(driver=driver, step=step, screenshot=screenshot, message=message)
    elif hook_name == "pytest_bdd_after_scenario":
        driver = get_active_driver_instance()
        scenario = args[2]

        report_test(driver=driver, scenario=scenario)

    if func:
        return pytestBDD_reporter(func)

    return pytestBDD_reporter


def report_step(driver, step, screenshot, message):
    """Report pytest-bdd  step"""
    driver.report().disable_reports(False)
    step_description = "{} {}".format(step.keyword, step.name)
    driver.report().step(
        description=step_description,
        message=message,
        passed=not step.failed,
        screenshot=screenshot,
    )
    driver.report().disable_reports(True)


def report_test(driver, scenario):
    """Report pytest-bdd scenario"""
    driver.report().disable_reports(False)
    test_name = scenario.name
    driver.report().test(name=test_name, passed=not scenario.failed)
    driver.report().disable_reports(True)
    driver.report().disable_reports(True)
