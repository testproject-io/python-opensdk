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

import logging
import os
from functools import wraps

from src.testproject.helpers.activesessionhelper import get_active_driver_instance
from src.testproject.sdk.exceptions import SdkException


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
            os.environ["TP_DISABLE_AUTO_REPORTING"] = "True"

            driver = None
            try:
                driver = get_active_driver_instance()
            except SdkException as err:
                logging.error(f"No valid WebDriver found: {err} - Reports are disabled!")

            if driver is not None:

                # Update job name as soon as possible.
                context = args[0]
                # Check if the context has a feature attribute which is not None to avoid error when decorator
                # is used on a method with a different param.
                if hasattr(context, "feature") and context.feature and not hasattr(context, "tp_job_name_updated"):
                    # Update the job name
                    driver.update_job_name(context.feature.name)
                    context.tp_job_name_updated = True

                # Report step or test based on the constant hook name.
                # Behave always calls the methods with the arguments in the following order: (context, step/scenario).
                hook_name = _func.__name__
                if hook_name == "after_step":
                    step = args[1]
                    report_step(driver=driver, step=step, screenshot=screenshot)
                elif hook_name == "after_scenario":
                    scenario = args[1]
                    report_test(driver=driver, scenario=scenario)

            return _func(*args, **kwargs)

        return wrapper

    if func:
        return _behave_reporter(func)

    return _behave_reporter


def report_step(driver, step, screenshot):
    """Report behave step"""
    step_description = "{} {}".format(step.keyword, step.name)
    step_status = True if step.status == "passed" else False
    step_message = (
        "{} {}".format(type(step.exception).__name__, str(step.exception)) if not step_status else step_description
    )
    driver.report().step(
        description=step_description,
        message=step_message,
        passed=step_status,
        screenshot=screenshot,
    )


def report_test(driver, scenario):
    """Report behave scenario"""
    test_name = scenario.name
    test_status = True if scenario.status == "passed" else False
    driver.report().test(name=test_name, passed=test_status)
