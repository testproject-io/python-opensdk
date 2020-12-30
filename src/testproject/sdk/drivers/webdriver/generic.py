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

from packaging import version
from src.testproject.enums import EnvironmentVariable
from src.testproject.helpers import ReportHelper, LoggingHelper, ConfigHelper, AddonHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages.agentstatusresponse import AgentStatusResponse
from src.testproject.sdk.exceptions import SdkException, AgentConnectException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import GenericCommandExecutor
from src.testproject.sdk.internal.reporter import Reporter
from src.testproject.sdk.internal.session import AgentSession


class Generic:
    """Used to create a new generic driver instance

    Args:
        token (str): The developer token used to communicate with the agent
        project_name (str): Project name to report
        job_name (str): Job name to report
        disable_reports (bool): set to True to disable all reporting (no report will be created on TestProject)
    """

    __instance = None

    MIN_GENERIC_DRIVER_SUPPORTED_VERSION = "0.64.40"

    def __init__(
        self,
        token: str = None,
        project_name: str = None,
        job_name: str = None,
        disable_reports: bool = False,
    ):
        if Generic.__instance is not None:
            raise SdkException("A driver session already exists")

        LoggingHelper.configure_logging()

        self._token = token if token is not None else ConfigHelper.get_developer_token()

        agent_status_response: AgentStatusResponse = AgentClient.get_agent_version(
            self._token
        )

        if version.parse(agent_status_response.tag) < version.parse(
            Generic.MIN_GENERIC_DRIVER_SUPPORTED_VERSION
        ):
            raise AgentConnectException(
                f"Your current Agent version {agent_status_response.tag} does not support the Generic driver. "
                f"Please upgrade your Agent to the latest version and try again"
            )
        else:
            logging.info(
                f"Current Agent version {agent_status_response.tag} does support Generic driver"
            )

        self.session_id = None

        if disable_reports:
            # Setting the project and job name to empty strings will cause the Agent to not initialize a report
            self._project_name = ""
            self._job_name = ""
        else:
            self._project_name = (
                project_name
                if project_name is not None
                else ReportHelper.infer_project_name()
            )
            self._job_name = (
                job_name if job_name is not None else ReportHelper.infer_job_name()
            )

        report_settings = ReportSettings(self._project_name, self._job_name)

        capabilities = {"platformName": "ANY"}

        self._agent_client: AgentClient = AgentClient(token=self._token, capabilities=capabilities,
                                                      report_settings=report_settings)

        self._agent_session: AgentSession = self._agent_client.agent_session

        self.command_executor = GenericCommandExecutor(agent_client=self._agent_client)

        Generic.__instance = self

    @classmethod
    def instance(cls):
        """Returns the singleton instance of the driver object"""
        return Generic.__instance

    def start_session(self, capabilities, browser_profile=None):
        """Sets capabilities and sessionId obtained from the Agent when creating the original session."""
        self.session_id = self._agent_session.session_id
        logging.info(f"Session ID is {self.session_id}")

    def report(self) -> Reporter:
        """Enables access to the TestProject reporting actions from the driver object"""
        return Reporter(self.command_executor)

    def addons(self) -> AddonHelper:
        """Enables access to the TestProject addon execution actions from the driver object

        Returns:
            AddonHelper: object giving access to addon proxy methods
        """
        return AddonHelper(self._agent_client, self.command_executor)

    def quit(self):
        """Quits the driver and stops the session with the Agent, cleaning up after itself."""
        # Report any left over driver command reports
        self.command_executor.clear_stash()

        # Report test explicitly as this is not done automatically
        self.command_executor.report_test()

        # Make instance available again
        Generic.__instance = None

        # Stop the Agent client
        self.command_executor.agent_client.stop()

        # Clean up any environment variables set in the decorator
        for env_var in [
            EnvironmentVariable.TP_TEST_NAME,
            EnvironmentVariable.TP_PROJECT_NAME,
            EnvironmentVariable.TP_JOB_NAME,
        ]:
            EnvironmentVariable.remove(env_var)
