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
import inspect

from selenium.webdriver.remote.command import Command

from src.testproject.classes import StepSettings
from src.testproject.enums import TakeScreenshotConditionType
from src.testproject.helpers import ReportHelper
from src.testproject.helpers.step_helper import StepHelper
from src.testproject.rest.messages import DriverCommandReport, CustomTestReport
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers.redact_helper import RedactHelper


class ReportingCommandExecutor:
    """Class responsible for executing commands and reporting them

    Args:
        agent_client (AgentClient): Client used to communicate with the TestProject Agent
        command_executor: The command executor used to send WebDriver commands (Selenium or Appium)

    Attributes:
        _agent_client (AgentClient): Client used to communicate with the TestProject Agent
        _command_executor: The command executor used to send WebDriver commands (Selenium or Appium)
        _disable_reports (bool): True if all reporting is disabled, False otherwise
        _disable_auto_test_reports (bool): True if automatic reporting of tests is disabled, False otherwise
        _disable_command_reports (bool): True if driver command reporting is disabled, False otherwise
        _disable_redaction (bool): True if reporting steps should be redacted, False otherwise
        _stashed_command (DriverCommandReport): contains stashed driver command for preventing duplicates
        inside WebDriverWait
        _latest_known_test_name (str): contains latest known test name
        _excluded_test_names (list): contains a list of test names that should not be reported
    """

    def __init__(self, agent_client: AgentClient, command_executor, remote_connection):
        self._agent_client = agent_client
        self._command_executor = command_executor
        self._disable_reports = False
        self._disable_auto_test_reports = False
        self._disable_command_reports = False
        self._disable_redaction = False
        self._stashed_command = None
        self._latest_known_test_name = ReportHelper.infer_test_name()
        self._excluded_test_names = list()
        self._step_helper = StepHelper(remote_connection, agent_client.agent_session.dialect == "W3C")
        self._settings = StepSettings()

    @property
    def disable_reports(self) -> bool:
        """Getter for the disable_reports flag"""
        return self._disable_reports

    @disable_reports.setter
    def disable_reports(self, value: bool):
        """Setter for the disable_reports flag"""
        self._disable_reports = value

    @property
    def disable_auto_test_reports(self) -> bool:
        """Getter for the disable_auto_test_reports flag"""
        return self._disable_auto_test_reports

    @disable_auto_test_reports.setter
    def disable_auto_test_reports(self, value: bool):
        """Setter for the disable_auto_test_reports flag"""
        self._disable_auto_test_reports = value

    @property
    def disable_command_reports(self) -> bool:
        """Getter for the disable_command_reports flag"""
        return self._disable_command_reports

    @disable_command_reports.setter
    def disable_command_reports(self, value: bool):
        """Setter for the disable_command_reports flag"""
        self._disable_command_reports = value

    @property
    def disable_redaction(self) -> bool:
        """Getter for the disable_redaction flag"""
        return self._disable_redaction

    @disable_redaction.setter
    def disable_redaction(self, value: bool):
        """Setter for the disable_redaction flag"""
        self._disable_redaction = value

    @property
    def excluded_test_names(self) -> list:
        """Getter for the list of excluded test names"""
        return self._excluded_test_names

    @excluded_test_names.setter
    def excluded_test_names(self, value: list):
        """Setter for the list of excluded test names"""
        self._excluded_test_names = value

    @property
    def agent_client(self):
        """Getter for the Agent client associated with this connection"""
        return self._agent_client

    @property
    def settings(self):
        """Getter for the settings for auto step reporting defined by the user."""
        return self._settings

    @settings.setter
    def settings(self, value: StepSettings):
        """Setter for the settings object."""
        self._settings = value

    @property
    def step_helper(self):
        """Getter for the StepHelper object."""
        return self._step_helper

    @property
    def test_name(self) -> str:
        """Getter for the latest known test name"""
        return self._latest_known_test_name

    @test_name.setter
    def test_name(self, new_name: str):
        """Setter for the latest known test name"""
        self._latest_known_test_name = new_name

    def _report_command(self, command: str, params: dict, result: dict, passed: bool):
        """Reports a driver command to the TestProject platform

        Args:
            command (str): The driver command to execute
            params (dict): Named parameters to send with the command as its JSON payload
            result (dict): The response returned by the Selenium remote webdriver server
            passed (bool): True if the command execution was successful, False otherwise
        """
        if command == Command.QUIT:
            if not self.disable_auto_test_reports:
                self.report_test()
            return  # This ensures that the actual driver.quit() command is not included in the report

        if not self._disable_redaction:
            params = RedactHelper(self).redact_command(command, params)

        # If the command is executed as part of a wait loop, we don't want to report it every time
        self._is_webdriverwait = False

        # See if the command is executed inside a wait loop
        for frame in inspect.stack().__reversed__():
            if str(frame.filename).find("wait.py") > 0:
                self._is_webdriverwait = True
                break

        # Invert result is set?
        passed = not passed if self.settings.invert_result else passed

        driver_command_report = DriverCommandReport(command, params, result, passed)

        # Is screenshot needed?
        take_screenshot = False
        if self.settings.screenshot_condition is TakeScreenshotConditionType.Failure and not passed:
            take_screenshot = True
        elif self.settings.screenshot_condition is TakeScreenshotConditionType.Success and passed:
            take_screenshot = True
        elif self.settings.screenshot_condition is TakeScreenshotConditionType.Always:
            take_screenshot = True

        if take_screenshot:
            driver_command_report.screenshot = self.create_screenshot()

        if self._is_webdriverwait:
            if not self._disable_reports and not self.disable_command_reports:
                # Only stash the command for reporting later when driver command reporting is enabled
                self._stashed_command = driver_command_report
            return  # Do not report the command right away

        if not self._disable_reports and not self.disable_command_reports:
            if self._stashed_command is not None:
                # report the stashed command and clear it
                self.agent_client.report_driver_command(self._stashed_command)
                self._stashed_command = None
            # report the current command
            self.agent_client.report_driver_command(driver_command_report)

    def update_known_test_name(self):
        """Infers the current test name and if different from the latest known test name, reports a test"""
        current_test_name = ReportHelper.infer_test_name()

        # Actions inside a unittest tearDown or tearDownClass method should be reported as part of the test
        in_unittest_teardown = ReportHelper.find_unittest_teardown()

        if (
            current_test_name not in [self._latest_known_test_name, "Unnamed Test"]
            and not in_unittest_teardown
        ):
            # the name of the test method has changed and we're not inside a unittest teardown method,
            # so we need to report a test
            if not self.disable_auto_test_reports:
                self.report_test()
            # update the latest known test name for future reports
            self._latest_known_test_name = current_test_name

    def report_test(self):
        """Sends a test report to the Agent if this option is not explicitly disabled
        """

        if not self._latest_known_test_name == "Unnamed Test":

            # only report those tests that have been identified as one when their names were inferred
            if self._disable_reports:
                # test reporting has been disabled by the user
                logging.debug(f"Test [{self._latest_known_test_name}] - [Passed]")
                return

            if self._latest_known_test_name in self._excluded_test_names:
                # test has been marked as 'to be excluded, so do not report it
                logging.debug(
                    f"Test [{self._latest_known_test_name}] - Reporting skipped (marked as 'To be excluded')"
                )
                return

            custom_test_report = CustomTestReport(
                name=self._latest_known_test_name, passed=True
            )
            self.agent_client.report_test(custom_test_report)

    def create_screenshot(self) -> str:
        """Creates a screenshot (PNG) and returns it as a base64 encoded string

        Returns:
            str: The base64 encoded screenshot in PNG format (or None if screenshot taking fails)
        """
        create_screenshot_params = {
            "sessionId": self.agent_client.agent_session.session_id
        }
        create_screenshot_response = self._command_executor.execute(
            Command.SCREENSHOT, create_screenshot_params, True
        )
        try:
            return create_screenshot_response["value"]
        except KeyError as ke:
            logging.error(f"Error occurred creating a screenshot: {ke}")
            logging.error(
                f"Response from RemoteWebDriver: {create_screenshot_response}"
            )
            return None

    def clear_stash(self):
        """Reports stashed command if there is one left. Should be called when session ends to prevent
           wait-related commands from not being reported.
        """
        if not self._disable_reports and not self.disable_command_reports:
            if self._stashed_command is not None:
                # report the stashed command and clear it
                self.agent_client.report_driver_command(self._stashed_command)
                self._stashed_command = None

    def is_command_passed(self, response: dict) -> bool:
        """Determine command result based on response using state and status.

        Args:
            response (dict): The response returned by the Selenium remote webdriver server

        Returns:
            bool: True if passed, otherwise False.
        """
        # Both None and 0 response status values indicate command execution was OK
        return True if response.get("status") in [None, 0] else False
