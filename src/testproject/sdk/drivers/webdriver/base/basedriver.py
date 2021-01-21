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

from src.testproject.classes import StepSettings
from src.testproject.enums import EnvironmentVariable
from src.testproject.helpers import ReportHelper, LoggingHelper, ConfigHelper, AddonHelper
from src.testproject.rest import ReportSettings
from src.testproject.sdk.exceptions import SdkException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import CustomCommandExecutor
from src.testproject.sdk.internal.reporter import Reporter
from src.testproject.sdk.internal.session import AgentSession
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
import os


class BaseDriver(RemoteWebDriver):
    """Base class with common functions for all web browser types

    Args:
        capabilities (dict): Automation session desired capabilities and options
        token (str): Developer token to be used to communicate with the Agent
        projectname (str): Project name to report
        jobname (str): Job name to report
        disable_reports (bool): set to True to disable all reporting (no report will be created on TestProject)

    Attributes:
        _agent_client (AgentClient): client responsible for communicating with the TestProject agent
        _agent_session (AgentSession): stores properties of the current agent session
        command_executor (CustomCommandExecutor): the HTTP command executor used to send instructions
        to remote WebDriver
        w3c (bool): indicates whether or not the driver instance uses the W3C dialect
        session_id (str): contains the current session ID
    """

    __instance = None

    def __init__(
        self,
        capabilities: dict,
        token: str,
        projectname: str,
        jobname: str,
        disable_reports: bool,
    ):

        if BaseDriver.__instance is not None:
            raise SdkException("A driver session already exists")

        LoggingHelper.configure_logging()

        if token is not None:
            logging.info(f"Token used as specified in constructor: {token}")

        self._token = token if token is not None else ConfigHelper.get_developer_token()

        if disable_reports:
            # Setting the project and job name to empty strings will cause the Agent to not initialize a report
            self._projectname = ""
            self._jobname = ""
        else:
            self._projectname = (
                projectname
                if projectname is not None
                else ReportHelper.infer_project_name()
            )
            self._jobname = (
                jobname if jobname is not None else ReportHelper.infer_job_name()
            )

        self._agent_client: AgentClient = AgentClient(
            token=self._token,
            capabilities=capabilities,
            report_settings=ReportSettings(self._projectname, self._jobname),
        )
        self._agent_session: AgentSession = self._agent_client.agent_session
        self.w3c = True if self._agent_session.dialect == "W3C" else False

        # Create a custom command executor to enable:
        # - automatic logging capabilities
        # - customized reporting settings
        self.command_executor = CustomCommandExecutor(
            agent_client=self._agent_client,
            remote_server_addr=self._agent_session.remote_address,
        )

        self.command_executor.disable_reports = disable_reports

        # Disable automatic command and test reports if Behave reporting is enabled.
        if os.getenv("TP_DISABLE_AUTO_REPORTING") == "True":
            self.command_executor.disable_command_reports = True
            self.command_executor.disable_auto_test_reports = True

        RemoteWebDriver.__init__(
            self,
            command_executor=self.command_executor,
            desired_capabilities=self._agent_session.capabilities,
        )

        BaseDriver.__instance = self

    @classmethod
    def instance(cls):
        """Returns the singleton instance of the driver object"""
        return cls.__instance

    @property
    def step_settings(self):
        return self.command_executor.settings

    @step_settings.setter
    def step_settings(self, step_settings: StepSettings):
        self.command_executor.settings = step_settings

    def start_session(self, capabilities, browser_profile=None):
        """Sets capabilities and sessionId obtained from the Agent when creating the original session."""
        self.session_id = self._agent_session.session_id
        logging.info(f"Session ID is {self.session_id}")

    def report(self) -> Reporter:
        """Enables access to the TestProject reporting actions from the driver object

        Returns:
            Reporter: object giving access to reporting methods
        """
        return Reporter(self.command_executor)

    def addons(self) -> AddonHelper:
        """Enables access to the TestProject addon execution actions from the driver object

        Returns:
            AddonHelper: object giving access to addon proxy methods
        """
        return AddonHelper(self._agent_client, self.command_executor)

    def quit(self):
        """Quits the driver and stops the session with the Agent, cleaning up after itself"""
        # Report any left over driver command reports
        self.command_executor.clear_stash()

        # Make instance available again
        BaseDriver.__instance = None

        try:
            RemoteWebDriver.quit(self)
        except Exception:
            pass

        # Stop the Agent client
        self.command_executor.agent_client.stop()

        # Clean up any environment variables set in the decorator
        for env_var in [
            EnvironmentVariable.TP_TEST_NAME,
            EnvironmentVariable.TP_PROJECT_NAME,
            EnvironmentVariable.TP_JOB_NAME,
        ]:
            EnvironmentVariable.remove(env_var)
