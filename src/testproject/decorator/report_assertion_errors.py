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


import os
import re
import sys
import traceback
from functools import wraps

from src.testproject.helpers.activesessionhelper import get_active_driver_instance


def report_assertion_errors(func=None, *, screenshot: bool = False):
    """Enables automatic logging of failed assertions, including a screenshot when screenshot argument is True."""

    def _report_assertion_errors(_func):
        @wraps(_func)
        def wrapper(*args, **kwargs):
            try:
                return _func(*args, **kwargs)
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
                driver = get_active_driver_instance()
                message = f"Assertion failed on line {line} in {function}"
                description, message = __handle_step_report_details(description, message)
                driver.report().step(
                    description=description,
                    message=f"Assertion failed on line {line} in {function}",
                    passed=False,
                    screenshot=screenshot,
                )
                # raise the AssertionError again to make the test execution fail as intended
                raise ae

        return wrapper

    if func:
        return _report_assertion_errors(func)

    return _report_assertion_errors


def __handle_step_report_details(description, message):
    """Handles the assertions description.

    AssertionError from pytest can contain multiple lines separated with '\n + ' between each line.
    The first line of the AssertionError will be the description, any additional lines will be added to the message.
    """
    inner_description = re.search(r"AssertionError\('(.*)'\)", description)
    if inner_description:
        inner_description = inner_description.group(1).replace('\\n', os.linesep).split(' + ')
        description = 'Assertion failed {{' + inner_description[0] + '}}'
        if len(inner_description) > 1:
            message += os.linesep
            for line in inner_description[1:]:
                message += line
    return description, message
