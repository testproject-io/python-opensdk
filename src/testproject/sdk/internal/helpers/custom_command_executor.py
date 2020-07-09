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
from selenium.webdriver.remote.remote_connection import RemoteConnection

from src.testproject.helpers import ReportHelper
from src.testproject.rest.messages import DriverCommandReport, CustomTestReport
from src.testproject.sdk.internal.agent import AgentClient


class CustomCommandExecutor(RemoteConnection):
    """Extension of the Selenium RemoteConnection (command_executor) class

        Args:
            agent_client (AgentClient): Client used to communicate with the TestProject Agent
            remote_server_addr (str): Remote server (Agent) address

        Attributes:
            _agent_client (AgentClient): Client used to communicate with the TestProject Agent
            _disable_reports (bool): True if all reporting is disabled, False otherwise
            _disable_auto_test_reports (bool): True if automatic reporting of tests is disabled, False otherwise
            _disable_command_reports (bool): True if driver command reporting is disabled, False otherwise
            _disable_redaction (bool): True if reporting steps should be redacted, False otherwise
            _stashed_command (DriverCommandReport): contains stashed driver command for preventing duplicates
            inside WebDriverWait
            _previous_test_name (str): contains latest known test name
    """

    def __init__(self, agent_client: AgentClient, remote_server_addr: str):
        super().__init__(remote_server_addr=remote_server_addr)
        self._agent_client = agent_client
        self._disable_reports = False
        self._disable_auto_test_reports = False
        self._disable_command_reports = False
        self._disable_redaction = False
        self._stashed_command = None
        self._latest_known_test_name = (
            ReportHelper.infer_test_name()
        )  # Avoids having to do null checks

        self.w3c = agent_client.agent_session.dialect == "W3C"

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
    def agent_client(self):
        """Getter for the Agent client associated with this connection"""
        return self._agent_client

    def execute(self, command: str, params: dict, skip_reporting: bool = False):
        """Execute a Selenium command

        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload
            skip_reporting (bool): True if command should not be reported to Agent, False otherwise

        Returns:
            response: Response returned by the Selenium remote webdriver server
        """
        self.update_known_test_name()

        response = super().execute(command=command, params=params)

        result = response.get("value")

        passed = True if response.get("status") is None else False

        if not skip_reporting:
            self._report_command(command, params, result, passed)

        return response

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
            params = self._redact_command(command, params)

        driver_command_report = DriverCommandReport(command, params, result, passed)

        self._is_webdriverwait = False

        # See if the command is executed inside a wait loop
        for frame in inspect.stack().__reversed__():
            if str(frame.filename).find("wait.py") > 0:
                self._is_webdriverwait = True
                break

        if self._is_webdriverwait:
            # Save the driver command to report it later once we're not in the wait loop anymore
            self._stashed_command = driver_command_report
            return

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

        if self._latest_known_test_name != current_test_name:
            # the name of the test method has changed, report a test
            if not self.disable_auto_test_reports:
                self.report_test()
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

            custom_test_report = CustomTestReport(
                name=self._latest_known_test_name, passed=True
            )
            self.agent_client.report_test(custom_test_report)

    def _redact_command(self, command: str, params: dict):
        """Redacts sensitive contents (passwords) so they do not appear in the reports

        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload

        Returns:
            dict: A redacted version of the dictionary, where password values are replaced by '****'
        """
        if command == Command.SEND_KEYS_TO_ELEMENT or command == Command.SEND_KEYS_TO_ACTIVE_ELEMENT:
            element_id = params["id"]
            get_attribute_params = {
                "sessionId": self.agent_client.agent_session.session_id,
                "id": element_id,
                "name": "type",
            }
            get_attribute_response = self.execute(Command.GET_ELEMENT_ATTRIBUTE, get_attribute_params, True)
            if get_attribute_response["value"] == "password":
                params["text"] = "***"
                params["value"] = list("***")
        return params

    def create_screenshot(self) -> str:
        """Creates a screenshot (PNG) and returns it as a base64 encoded string

        Returns:
            str: The base64 encoded screenshot in PNG format (or None if screenshot taking fails)
        """
        create_screenshot_params = {"sessionId": self.agent_client.agent_session.session_id}
        create_screenshot_response = self.execute(Command.SCREENSHOT, create_screenshot_params, True)
        try:
            return create_screenshot_response["value"]
        except KeyError as ke:
            logging.error(f"Error occurred creating a screenshot: {ke}")
            logging.error(f"Response from RemoteWebDriver: {create_screenshot_response}")
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
