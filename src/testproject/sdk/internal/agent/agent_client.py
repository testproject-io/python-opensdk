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
import queue
import threading
import uuid
from enum import Enum, unique
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from packaging import version
from requests import HTTPError

from src.testproject.classes import ActionExecutionResponse
from src.testproject.classes.resultfield import ResultField
from src.testproject.enums import ExecutionResultType
from src.testproject.executionresults import OperationResult
from src.testproject.helpers import ConfigHelper, SeleniumHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages import (
    SessionRequest,
    SessionResponse,
    DriverCommandReport,
    StepReport,
    CustomTestReport,
    AddonExecutionResponse)
from src.testproject.rest.messages.agentstatusresponse import AgentStatusResponse
from src.testproject.sdk.addons import ActionProxy
from src.testproject.sdk.exceptions import (
    SdkException,
    AgentConnectException,
    InvalidTokenException,
    ObsoleteVersionException,
)
from src.testproject.sdk.exceptions.addonnotinstalled import AddonNotInstalledException
from src.testproject.sdk.internal.session import AgentSession
from src.testproject.tcp import SocketManager


class AgentClient:
    """Client used to communicate with the TestProject Agent process

    Args:
        token (str): The development token used to communicate with the Agent
        capabilities (dict): Additional options to be applied to the driver instance
        report_settings (ReportSettings): Settings (project name, job name) to be included in the report

    Attributes:
        _remote_address (str): The Agent endpoint
        _capabilities (dict): Additional options to be applied to the driver instance
        _agent_session (AgentSession): stores properties of the current agent session
        _token (str): The development token used to authenticate with the Agent
        _report_settings (ReportSettings): Settings (project name, job name) to be included in the report
        _queue (queue.Queue): queue holding reports to be sent to Agent in separate thread
    """

    REPORTS_QUEUE_TIMEOUT = 10

    # Minimum Agent version number that supports session reuse
    MIN_SESSION_REUSE_CAPABLE_VERSION = "0.64.20"

    # Class variable containing the current known Agent version
    __agent_version: str = None

    def __init__(self, token: str, capabilities: dict, report_settings: ReportSettings):
        self._remote_address = ConfigHelper.get_agent_service_address()
        self._capabilities = capabilities
        self._agent_session = None
        self._token = token
        self._report_settings = report_settings
        self._queue = queue.Queue()

        self._running = True
        self._reporting_thread = threading.Thread(
            target=self.__report_worker, daemon=True
        )
        self._reporting_thread.start()

        if not self.__start_session():
            raise SdkException("Failed to start development mode session")

    @property
    def agent_session(self):
        """Getter for the Agent session object"""
        return self._agent_session

    def __start_session(self) -> bool:
        """Starts a new development session with the Agent

        Returns:
            bool: True if the session started successfully, False otherwise
        """
        sdk_version = ConfigHelper.get_sdk_version()

        logging.info(f"SDK version: {sdk_version}")

        start_session_response = self._request_session_from_agent()

        AgentClient.__agent_version = start_session_response.agent_version

        self._agent_session = AgentSession(
            start_session_response.server_address,
            start_session_response.session_id,
            start_session_response.dialect,
            start_session_response.capabilities,
        )

        SocketManager.instance().open_socket(
            self._remote_address, start_session_response.dev_socket_port
        )

        logging.info("Development session started...")
        return True

    @staticmethod
    def can_reuse_session() -> bool:
        """Determine whether the current Agent version supports session reuse

        Returns:
             bool: True if Agent supports session reuse, False otherwise
        """
        if AgentClient.__agent_version is None:
            return False

        return version.parse(
            AgentClient.__agent_version
        ) >= version.parse(AgentClient.MIN_SESSION_REUSE_CAPABLE_VERSION)

    def _request_session_from_agent(self) -> SessionResponse:
        """Creates and sends a session request object

        Returns:
            SessionResponse: object containing the response to the session request
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
            logging.error(
                f"Could not start new session on {self._remote_address}. Is your Agent running?"
            )
            logging.error(
                "You can download the TestProject Agent from https://app.testproject.io/#/agents"
            )
            raise AgentConnectException(
                f"Connection error trying to connect to Agent on {self._remote_address}"
            )

        if not response.passed:
            self.__handle_new_session_error(response)

        # The generic driver returns a partial response, so we have to create some fields ourselves
        session_id = response.data.get("sessionId", uuid.uuid4())

        dialect = response.data.get("dialect")

        capabilities = response.data.get("capabilities", {})

        agent_version = response.data.get("version")

        # If driver is Generic, supply None as the server address.
        server_address = response.data.get("serverAddress")

        start_session_response = SessionResponse(
            dev_socket_port=response.data["devSocketPort"],
            server_address=server_address,
            session_id=session_id,
            dialect=dialect,
            capabilities=capabilities,
            agent_version=agent_version,
        )
        return start_session_response

    def send_request(self, method, path, body=None) -> OperationResult:
        """Sends HTTP request to Agent

        Args:
            method (str): HTTP method (GET, POST, ...)
            path (str): Relative API route path
            body (dict): Request body

        Returns:
            OperationResult: contains result of the sent request
        """
        with requests.Session() as session:
            if method == "GET":
                response = session.get(path, headers={"Authorization": self._token})
            elif method == "POST":
                response = session.post(
                    path, headers={"Authorization": self._token}, json=body
                )
            elif method == "DELETE":
                response = session.delete(path, headers={"Authorization": self._token})
            else:
                raise SdkException(
                    f"Unsupported HTTP method {method} in send_request()"
                )

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
            return OperationResult(False, response.status_code,
                                   response_json.get('message', str(http_error)),
                                   response_json if response_json else None)

    def send_action_execution_request(
        self, codeblock_guid: str, body: dict
    ) -> ActionExecutionResponse:
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
                ExecutionResultType.Passed
                if response.data["resultType"] == "Passed"
                else ExecutionResultType.Failed
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
                urljoin(
                    ConfigHelper.get_agent_service_address(), Endpoint.GetStatus.value
                ),
                headers={"Authorization": token},
            )

        try:
            response.raise_for_status()
            try:
                response_json = response.json()
                agent_version = response_json["tag"]
            except ValueError:
                raise SdkException(
                    "Could not parse Agent status response: no JSON response body present"
                )
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

        queue_item = QueueItem(
            report_as_json=driver_command_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportDriverCommand.value),
            token=self._token,
        )

        self._queue.put(queue_item, block=False)

    def report_step(self, step_report: StepReport):
        """Sends step report to the Agent

        Args:
            step_report (StepReport): object containing the step to be reported
        """

        queue_item = QueueItem(
            report_as_json=step_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportStep.value),
            token=self._token,
        )

        self._queue.put(queue_item, block=False)

    def report_test(self, test_report: CustomTestReport):
        """Sends test report to the Agent

        Args:
            test_report (CustomTestReport): object containing the test to be reported
        """

        queue_item = QueueItem(
            report_as_json=test_report.to_json(),
            url=urljoin(self._remote_address, Endpoint.ReportTest.value),
            token=self._token,
        )

        self._queue.put(queue_item, block=False)

    def stop(self):
        """Send all remaining report items in the queue to TestProject"""
        # Send a stop signal to the thread worker
        self._running = False

        # Send a final, empty, report to the queue to ensure that
        # the 'running' condition is evaluated one last time
        self._queue.put(
            QueueItem(report_as_json=None, url=None, token=self._token), block=False
        )

        # Wait until all items have been reported or timeout passes
        self._reporting_thread.join(timeout=self.REPORTS_QUEUE_TIMEOUT)
        if self._reporting_thread.is_alive():
            # Thread is still alive, so there are unreported items
            logging.warning(
                f"There are {self._queue.qsize()} unreported items in the queue"
            )

        if not AgentClient.can_reuse_session():
            SocketManager.instance().close_socket()

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
        )

        if operation_result.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f'Action [{action.proxydescriptor.classname}] in addon [{action.proxydescriptor.guid}]'
                          f' is not installed in your account.')
            raise AddonNotInstalledException

        return AddonExecutionResponse(execution_result_type=(ExecutionResultType.Passed
                                                             if operation_result.data["resultType"] == "Passed"
                                                             else ExecutionResultType.Failed),
                                      message=operation_result.data["message"],
                                      fields=[ResultField(**field) for field in operation_result.data['fields']])

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

    def __handle_new_session_error(self, response: OperationResult):
        """ Handles errors occurring on creation of a new session with the Agent

        Args:
            response (OperationResult): response from the Agent
        """
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.error(
                "Failed to initialize a session with the Agent - invalid developer token supplied"
            )
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

    def __report_worker(self):
        """Worker method that is polling the queue for items to report"""
        while self._running or self._queue.qsize() > 0:

            item = self._queue.get()
            if isinstance(item, QueueItem):
                item.send()
            else:
                logging.warning(
                    f"Unknown object of type {type(item)} found on queue, ignoring it.."
                )
            self._queue.task_done()


class QueueItem:
    """Helper class representing an item to be reported

    Args:
        report_as_json (dict): JSON payload representing the item to be reported
        url (str): Agent endpoint the payload should be POSTed to
        token (str): Token used to authenticate with the Agent

    Attributes:
        _report_as_json (dict): JSON payload representing the item to be reported
        _url (str): Agent endpoint the payload should be POSTed to
        _token (str): Token used to authenticate with the Agent
    """

    def __init__(self, report_as_json: dict, url: str, token: str):
        self._report_as_json = report_as_json
        self._url = url
        self._token = token

    def send(self):
        """Send a report item to the Agent"""
        if self._report_as_json is None and self._url is None:
            # Skip empty queue items put in the queue on stop()
            return

        with requests.Session() as session:
            response = session.post(
                self._url,
                headers={"Authorization": self._token},
                json=self._report_as_json,
            )
            try:
                response.raise_for_status()
            except HTTPError:
                logging.error(
                    f"Reporting to TestProject returned an HTTP {response.status_code}"
                )
                logging.error(f"Response from Agent: {response.text}")


@unique
class Endpoint(Enum):
    DevelopmentSession = "/api/development/session"
    ActionExecution = "/api/codeblocks/executions"
    ReportDriverCommand = "/api/development/report/command"
    ReportStep = "/api/development/report/step"
    ReportTest = "/api/development/report/test"
    AddonExecution = "/api/addons/executions"
    GetStatus = "/api/status"
