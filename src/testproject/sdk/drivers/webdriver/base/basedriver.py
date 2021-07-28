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

from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from src.testproject.classes import StepSettings
from src.testproject.enums import EnvironmentVariable
from src.testproject.enums.report_type import ReportType
from src.testproject.helpers import (
    ReportHelper,
    LoggingHelper,
    ConfigHelper,
    AddonHelper,
)
from src.testproject.rest import ReportSettings
from src.testproject.sdk.exceptions import SdkException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import CustomCommandExecutor
from src.testproject.sdk.internal.reporter import Reporter
from src.testproject.sdk.internal.session import AgentSession


class BaseDriver(RemoteWebDriver):
    """Base class with common functions for all web browser types

    Args:
        capabilities (dict): Automation session desired capabilities and options
        token (str): Developer token to be used to communicate with the Agent
        project_name (str): Project name to report
        job_name (str): Job name to report
        disable_reports (bool): set to True to disable all reporting (no report will be created on TestProject)
        report_type (ReportType): Type of report to produce - cloud, local or both.

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
        project_name: str,
        job_name: str,
        disable_reports: bool,
        report_type: ReportType,
        agent_url: str,
        report_name: str,
        report_path: str,
    ):

        if BaseDriver.__instance is not None:
            raise SdkException("A driver session already exists")

        LoggingHelper.configure_logging()
        env_token = ConfigHelper.get_developer_token()
        if env_token is not None:
            if token is not None:
                logging.info(
                    "Found TP_DEV_TOKEN environment variable. Using its value as the development token "
                    "instead of the value in the driver constructor"
                )
            self._token = env_token
        elif token is not None:
            self._token = token
        else:
            logging.error("No developer token was found, did you set it in the TP_DEV_TOKEN environment variable?")
            logging.error(
                "You can get a developer token from https://app.testproject.io/#/integrations/sdk?lang=Python"
            )
            raise SdkException("No development token was provided")

        if disable_reports:
            # Setting the project and job name to empty strings will cause the Agent to not initialize a report
            self._project_name = ""
            self._job_name = ""
        else:
            self._project_name = project_name if project_name is not None else ReportHelper.infer_project_name()

            if job_name:
                self._job_name = job_name
            else:
                self._job_name = ReportHelper.infer_job_name()
                # Can update job name at runtime if not specified.
                os.environ[EnvironmentVariable.TP_UPDATE_JOB_NAME.value] = "True"

        self._agent_client: AgentClient = AgentClient(
            token=self._token,
            capabilities=capabilities,
            agent_url=agent_url,
            report_settings=ReportSettings(self._project_name, self._job_name, report_type, report_name, report_path),
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

    def pause(self, milliseconds: int):
        self.command_executor.pause(milliseconds)

    def update_job_name(self, job_name):
        """Updates the job name of the execution during runtime

        Args:
            job_name (str): updated job name to set for the execution.
        """
        self._agent_client.update_job_name(job_name=job_name)

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
