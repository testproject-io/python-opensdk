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
import uuid

from distutils.util import strtobool
from enum import Enum, unique
from http import HTTPStatus
from urllib.parse import urljoin, urlparse, ParseResult

import requests
import os
from requests import HTTPError

from src.testproject.classes import ActionExecutionResponse
from src.testproject.classes.resultfield import ResultField
from src.testproject.enums import ExecutionResultType
from src.testproject.enums.report_type import ReportType
from src.testproject.executionresults import OperationResult
from src.testproject.helpers import ConfigHelper, SeleniumHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages import (
    SessionRequest,
    SessionResponse,
    DriverCommandReport,
    StepReport,
    CustomTestReport,
    AddonExecutionResponse,
)
from src.testproject.rest.messages.agentstatusresponse import AgentStatusResponse
from src.testproject.sdk.addons import ActionProxy
from src.testproject.sdk.exceptions import (
    SdkException,
    AgentConnectException,
    InvalidTokenException,
    ObsoleteVersionException,
)
from src.testproject.sdk.exceptions.addonnotinstalled import AddonNotInstalledException
from src.testproject.sdk.internal.agent.agent_client_singleton import AgentClientSingleton
from src.testproject.sdk.internal.agent.reports_queue import ReportsQueue
from src.testproject.sdk.internal.agent.reports_queue_batch import ReportsQueueBatch
from src.testproject.sdk.internal.session import AgentSession
from src.testproject.tcp import SocketManager
from packaging import version


class AgentClient(metaclass=AgentClientSingleton):
    """Client used to communicate with the TestProject Agent process

    Args:
        token (str): The development token used to communicate with the Agent
        capabilities (dict): Additional options to be applied to the driver instance
        report_settings (ReportSettings): Settings (project name, job name) to be included in the report

    Attributes:
        _remote_address (str): The Agent endpoint
        _capabilities (dict): Additional options to be applied to the driver instance
        _agent_session (AgentSession): stores properties of the current agent session
        _agent_response (SessionResponse): Session initialization response.
        _token (str): The development token used to authenticate with the Agent
        _report_settings (ReportSettings): Settings (project name, job name) to be included in the report
        _queue (queue.Queue): queue holding reports to be sent to Agent in separate thread
    """

    # Minimum Agent version number that supports session reuse
    MIN_SESSION_REUSE_CAPABLE_VERSION = "0.64.20"

    # Minimum Agent version that supports local reports.
    MIN_LOCAL_REPORT_SUPPORTED_VERSION = "2.1.0"

    # Minimum Agent version that supports batch reporting.
    MIN_BATCH_REPORT_SUPPORTED_VERSION = "3.1.0"

    # Class variable containing the current known Agent version
    __agent_version: str = None

    def __init__(self, token: str, capabilities: dict, agent_url: str, report_settings: ReportSettings):
        self.agent_url = agent_url
        self._is_local_execution = True
        self._agent_session = None
        self._agent_response = None
        self._remote_address = agent_url if agent_url is not None else ConfigHelper.get_agent_service_address()
        self.__check_local_execution()
        self._report_settings = report_settings
        self._capabilities = capabilities
        self._token = token
        # Attempt to start the session
        self.__start_session()
        # Make sure local reports are supported
        self.__verify_local_reports_supported(report_settings.report_type)
        # Create reports queue
        if version.parse(self.__agent_version) >= version.parse(self.MIN_BATCH_REPORT_SUPPORTED_VERSION):
            url = urljoin(self._remote_address, Endpoint.ReportBatch.value)
            self._reports_queue = ReportsQueueBatch(token=token, url=url)
        else:
            self._reports_queue = ReportsQueue(token)

    @property
    def agent_session(self):
        """Getter for the Agent session object"""
        return self._agent_session

    @property
    def report_settings(self) -> ReportSettings:
        """Getter for the ReportSettings object"""
        return self._report_settings

    def __verify_local_reports_supported(self, report_type: ReportType):
        """Verify that target Agent supports local reports, otherwise throw an exception.

        Args:
            report_type (ReportType): Report type requested.

        Raises:
            AgentConnectException when local reports are not supported.
        """
        if report_type is ReportType.LOCAL and version.parse(self.__agent_version) < version.parse(
            self.MIN_LOCAL_REPORT_SUPPORTED_VERSION
        ):
            raise AgentConnectException(
                f"Target Agent version [{self.__agent_version}] doesn't support local reports."
                f" Upgrade the Agent to the latest version and try again."
            )

    def __start_session(self):
        """Starts a new development session with the Agent"""
        sdk_version = ConfigHelper.get_sdk_version()

        logging.info(f"SDK version: {sdk_version}")

        self._request_session_from_agent()

        self.log_warnings()

        AgentClient.__agent_version = self._agent_response.agent_version

        # Log the report URL is the returned URL is not empty
        if self._agent_response.local_report_url is not None and self._agent_response.local_report_url:
            parsed_report_url = urlparse(self._agent_response.local_report_url)
            report_url = ParseResult(
                scheme=parsed_report_url.scheme,
                netloc=f"{urlparse(self._remote_address).hostname}:{parsed_report_url.port}",
                path=parsed_report_url.path,
                params=parsed_report_url.params,
                query=parsed_report_url.query,
                fragment=parsed_report_url.fragment,
            ).geturl()

            logging.info("Report URL: " + report_url)

        self._agent_session = AgentSession(
            self._agent_response.server_address,
            self._agent_response.session_id,
            self._agent_response.dialect,
            self._agent_response.capabilities,
        )

        SocketManager.instance().open_socket(
            urlparse(self._remote_address).hostname,
            self._agent_response.dev_socket_port,
            self._agent_response.uuid,
        )

        logging.info("Development session started...")

    def log_warnings(self):
        """Log various warnings which might be returned from the agent"""
        if self._agent_response.warnings is not None:
            for warning in self._agent_response.warnings:
                logging.warning(warning)

    @staticmethod
    def can_reuse_session() -> bool:
        """Determine whether the current Agent version supports session reuse

        Returns:
             bool: True if Agent supports session reuse, False otherwise
        """
        if AgentClient.__agent_version is None:
            return False

        return version.parse(AgentClient.__agent_version) >= version.parse(
            AgentClient.MIN_SESSION_REUSE_CAPABLE_VERSION
        )

    def _request_session_from_agent(self):
        """Creates and sends a session request object

        Sets the SessionResponse: object containing the response to the session request
        """
        session_request = SessionRequest(self._capabilities, self._report_settings)

        logging.info(f"Session request: {session_request.to_json()}")

        try:
            response = self.send_request(
                "POST",
                urljoin(self._remote_address, Endpoint.DevelopmentSession.value),
                session_request.to_json(),
            )
        except requests.exceptions.ConnectionError:
            logging.error(f"Could not start new session on {self._remote_address}. Is your Agent running?")
            logging.error("You can download the TestProject Agent from https://app.testproject.io/#/agents")
            raise AgentConnectException(f"Connection error trying to connect to Agent on {self._remote_address}")

        if not response.passed:
            self.__handle_new_session_error(response)

        self._agent_response = SessionResponse(
            dev_socket_port=response.data["devSocketPort"],
            server_address=response.data.get("serverAddress"),
            session_id=response.data.get("sessionId", uuid.uuid4()),
            dialect=response.data.get("dialect"),
            capabilities=response.data.get("capabilities", {}),
            agent_version=response.data.get("version"),
            local_report=response.data.get("localReport"),
            local_report_url=response.data.get("localReportUrl"),
            uuid=response.data.get("uuid"),
            warnings=response.data.get("warnings"),
        )

    def update_job_name(self, job_name):
        """Sends HTTP request to Agent to update job name during runtime.

        Args:
            job_name (str): new job name to use for the current execution
        """
        if strtobool(os.getenv("TP_UPDATE_JOB_NAME")):
            logging.info(f"Updating job name to: {job_name}")
            try:
                response = self.send_request(
                    "PUT",
                    urljoin(self._remote_address, Endpoint.DevelopmentSession.value),
                    {"jobName": job_name},
                )
                if not response.passed:
                    logging.error("Failed to update job name")
            except requests.exceptions.RequestException:
                logging.error("Failed to update job name")

    def send_request(self, method, path, body=None, params=None) -> OperationResult:
        """Sends HTTP request to Agent

        Args:
            method (str): HTTP method (GET, POST, ...)
            path (str): Relative API route path
            body (dict): Request body
            params (dict): Request parameters

        Returns:
            OperationResult: contains result of the sent request
        """
        with requests.Session() as session:
            if params:
                session.params = params
            if method == "GET":
                response = session.get(path, headers={"Authorization": self._token})
            elif method == "POST":
                response = session.post(path, headers={"Authorization": self._token}, json=body)
            elif method == "DELETE":
                response = session.delete(path, headers={"Authorization": self._token})
            elif method == "PUT":
                response = session.put(path, headers={"Authorization": self._token}, json=body)
            else:
                raise SdkException(f"Unsupported HTTP method {method} in send_request()")

        response_json = {}
        # For some successful calls, the response body will be empty
        # Parsing it results in a ValueError, so we should handle this
        try:
            response_json = response.json()
        except ValueError:
            pass

        # Handling any HTTPError exceptions.
        try:
            response.raise_for_status()
            return OperationResult(True, response.status_code, "", response_json)
        except HTTPError as http_error:
            return OperationResult(
                False,
                response.status_code,
                response_json.get("message", str(http_error)),
                response_json if response_json else None,
            )

    def send_action_execution_request(self, codeblock_guid: str, body: dict) -> ActionExecutionResponse:
        """Sends HTTP request to Agent

        Args:
            codeblock_guid (str): The codeblock GUID to be executed
            body (dict): Parameters to be passed to the Agent

        Returns:
            ActionExecutionResponse: contains result of the sent execution request
        """

        response = self.send_request(
            "POST",
            urljoin(
                urljoin(self._remote_address, Endpoint.ActionExecution.value),
                codeblock_guid,
            ),
            body,
        )

        if not response.passed:
            result = ExecutionResultType.Failed
        else:
            result = (
                ExecutionResultType.Passed if response.data["resultType"] == "Passed" else ExecutionResultType.Failed
            )

        result_data = response.data["outputs"] if response.passed else None

        return ActionExecutionResponse(result, response.message, result_data)

    @staticmethod
    def get_agent_version(token: str):
        """Requests the current Agent status

        Args:
            token (str): The developer token used to communicate with the Agent

        Returns:
            AgentStatusResponse: contains the response to the sent Agent status request
        """

        with requests.Session() as session:
            response = session.get(
                urljoin(ConfigHelper.get_agent_service_address(), Endpoint.GetStatus.value),
                headers={"Authorization": token},
            )

        try:
            response.raise_for_status()
            try:
                response_json = response.json()
                agent_version = response_json["tag"]
            except ValueError:
                raise SdkException("Could not parse Agent status response: no JSON response body present")
            except KeyError:
                raise SdkException(
                    "Could not parse Agent status response: element 'tag' not found in JSON response body"
                )
        except HTTPError:
            raise AgentConnectException(
                f"Agent returned HTTP {response.status_code} when trying to retrieve Agent status"
            )

        return AgentStatusResponse(agent_version)

    def report_driver_command(self, driver_command_report: DriverCommandReport):
        """Sends command report to the Agent

        Args:
            driver_command_report: object containing the driver command to be reported
        """
        self._reports_queue.submit(
            report_as_json=driver_command_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportDriverCommand.value),
            block=False,
        )

    def report_step(self, step_report: StepReport):
        """Sends step report to the Agent

        Args:
            step_report (StepReport): object containing the step to be reported
        """

        self._reports_queue.submit(
            report_as_json=step_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportStep.value),
            block=False,
        )

    def report_test(self, test_report: CustomTestReport):
        """Sends test report to the Agent

        Args:
            test_report (CustomTestReport): object containing the test to be reported
        """

        self._reports_queue.submit(
            report_as_json=test_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportTest.value),
            block=False,
        )

    def execute_proxy(self, action: ActionProxy) -> AddonExecutionResponse:
        """Sends a custom action to the Agent
        Args:
            action (ActionProxy): The custom action to be executed
        Returns:
            AddonExecutionResponse: object containing the result of the action execution
        """

        # Sending proxy request...
        operation_result = self.send_request(
            "POST",
            urljoin(self._remote_address, Endpoint.AddonExecution.value),
            self._create_action_proxy_payload(action),
            {"skipReporting": "true"},  # Delegate reporting from Agent to SDK.
        )

        if operation_result.status_code == HTTPStatus.NOT_FOUND:
            logging.error(
                f"Action [{action.proxydescriptor.classname}] in addon [{action.proxydescriptor.guid}]"
                f" is not installed in your account."
            )
            raise AddonNotInstalledException

        return AddonExecutionResponse(
            execution_result_type=(
                ExecutionResultType.Passed
                if operation_result.data["resultType"] == "Passed"
                else ExecutionResultType.Failed
            ),
            message=operation_result.data["message"],
            fields=(
                []
                if not operation_result.data["fields"]
                else [ResultField(**field) for field in operation_result.data["fields"]]
            ),
        )

    @staticmethod
    def _create_action_proxy_payload(action: ActionProxy) -> dict:
        """Creates a payload dictionary that will be transformed to a action JSON request body
        Args:
            action (ActionProxy): The action for which a payload should be created
        Returns:
            dict: the payload dictionary used to request execution of an action
        """
        payload = {
            "guid": action.proxydescriptor.guid,
            "className": action.proxydescriptor.classname,
            "parameters": action.proxydescriptor.parameters,
        }
        if action.proxydescriptor.by is not None:
            payload["by"] = SeleniumHelper.create_addon_locator(
                action.proxydescriptor.by, action.proxydescriptor.by_value
            )
        return payload

    @staticmethod
    def __handle_new_session_error(response: OperationResult):
        """Handles errors occurring on creation of a new session with the Agent

        Args:
            response (OperationResult): response from the Agent
        """
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.error("Failed to initialize a session with the Agent - invalid developer token supplied")
            logging.error(
                "Get your developer token from https://app.testproject.io/#/integrations/sdk?lang=Python"
                " and set it in the TP_DEV_TOKEN environment variable"
            )
            raise InvalidTokenException(response.message)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            error_message = response.message if response.message else "Failed to start a new session!"
            raise SdkException(error_message)
        elif response.status_code == HTTPStatus.NOT_ACCEPTABLE:
            logging.error(
                f"Failed to initialize a session with the Agent - obsolete SDK version {ConfigHelper.get_sdk_version()}"
            )
            raise ObsoleteVersionException(response.message)
        else:
            logging.error("Failed to initialize a session with the Agent")
            raise AgentConnectException(
                f"Agent responded with HTTP status {response.status_code}: [{response.message}]"
            )

    def __check_local_execution(self):
        """Helper method which validates if the remote address supplied is local"""
        valid_hosts = ["127.0.0.1", "localhost", "0.0.0.0"]
        if urlparse(self._remote_address).hostname in valid_hosts:
            self._is_local_execution = True

    def stop(self):
        self._reports_queue.stop()
        if self._agent_response and self._agent_response.local_report and self._is_local_execution:
            logging.info(f"Execution Report: {self._agent_response.local_report}")


@unique
class Endpoint(Enum):
    DevelopmentSession = "/api/development/session"
    ActionExecution = "/api/codeblocks/executions"
    ReportDriverCommand = "/api/development/report/command"
    ReportStep = "/api/development/report/step"
    ReportTest = "/api/development/report/test"
    ReportBatch = "/api/development/report/batch"
    AddonExecution = "/api/addons/executions"
    GetStatus = "/api/status"
