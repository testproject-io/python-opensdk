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

import logging
import os

from src.testproject.classes import ElementSearchCriteria
from src.testproject.helpers import ReportHelper
from src.testproject.rest.messages import StepReport, CustomTestReport


class Reporter:
    """Exposes reporting actions to the WebDriver object

    Args:
        command_executor: the command executor associated with the driver

    Attributes:
        _command_executor: the command executor associated with the driver
    """

    def __init__(self, command_executor):
        self._command_executor = command_executor

    def step(
        self,
        description: str,
        message: str,
        passed: bool,
        screenshot: bool = False,
        element: ElementSearchCriteria = None,
        inputs: dict = None,
        outputs: dict = None,
    ):
        """Sends a step report to the Agent Client

        Args:
            description (str): The step description
            message (str): A message that goes with the step
            passed (bool): True if the step should be marked as passed, False otherwise
            screenshot (bool): True if a screenshot should be made, False otherwise
            element (ElementSearchCriteria): The step's element search criteria.
            inputs (dict): Input parameters associated with the step
            outputs (dict): Output parameters associated with the step
        """

        # First update the current test name and report a test if necessary
        self._command_executor.update_known_test_name()

        if not self._command_executor.disable_reports:

            step_report = StepReport(
                description,
                message,
                passed,
                self._command_executor.create_screenshot() if screenshot else None,
                element,
                inputs,
                outputs,
            )
            self._command_executor.agent_client.report_step(step_report)
        else:
            logging.debug(f"Step '{description}' {'passed' if passed else 'failed'}")

    def test(self, name: str = None, passed: bool = True, message: str = None):
        """Sends a test report to the Agent Client

        Args:
            name (str): The test name
            passed (bool): True if the test should be marked as passed, False otherwise
            message (str): A message that goes with the test
        """
        if not self._command_executor.disable_reports:
            if name is None:
                name = ReportHelper.infer_test_name()

            if not self._command_executor.disable_auto_test_reports:
                if os.getenv("RFW_SUPPRESS_WARNINGS", "false").casefold() != "true":
                    logging.warning(
                        "Automatic reporting is enabled, disable this using disable_reports flag "
                        "when creating a driver instance to avoid duplicates in the report"
                    )

            test_report = CustomTestReport(
                name=name,
                passed=passed,
                message=message,
            )

            self._command_executor.agent_client.report_test(test_report)

        else:
            logging.debug(f"Test '{name}' {'passed' if passed else 'failed'}")

    def disable_reports(self, disabled: bool):
        """Enables or disabled all reporting

        Args:
            disabled (bool): Set to True to disable all reporting to the Agent
        """
        self._command_executor.disable_reports = disabled

    def disable_auto_test_reports(self, disabled: bool):
        """Enables or disables automatically reporting a test to the Agent

        Args:
            disabled (bool): Set to True to disable automatically reporting a test to the Agent
        """
        self._command_executor.disable_auto_test_reports = disabled

    def disable_command_reports(self, disabled: bool):
        """Enables or disables driver command reporting

        Args:
            disabled (bool): Set to True to disable driver command reports being sent to the Agent.
        """
        self._command_executor.disable_command_reports = disabled

    def disable_redaction(self, disabled: bool):
        """Enables or disables driver command report redaction

        Args:
            disabled (bool): Set to True to disable driver command report redaction.
        """
        self._command_executor.disable_redaction = disabled

    def exclude_test_names(self, excluded_test_names: list):
        """Excludes a list of test names (as strings) from being reported

        Args:
            excluded_test_names: list of strings containing tests that should not be reported.
        """
        self._command_executor.excluded_test_names = excluded_test_names
