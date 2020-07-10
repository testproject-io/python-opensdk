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
import socket
from enum import Enum, unique

import requests
import threading
import queue
from requests import HTTPError

from src.testproject.classes import ActionExecutionResponse
from src.testproject.enums import ExecutionResultType
from src.testproject.executionresults import OperationResult
from src.testproject.helpers import ConfigHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages import (
    SessionRequest,
    SessionResponse,
    DriverCommandReport,
    StepReport,
    CustomTestReport,
)
from src.testproject.sdk.exceptions import SdkException
from src.testproject.helpers import SocketHelper
from src.testproject.sdk.internal.session import AgentSession


class AgentClient:
    """Client used to communicate with the TestProject Agent process

        Args:
            token (str): The development token used to communicate with the Agent
            capabilities (dict): Additional options to be applied to the driver instance
            reportsettings (ReportSettings): Settings (project name, job name) to be included in the report

        Attributes:
            _remote_address (str): The Agent endpoint
            _capabilities (dict): Additional options to be applied to the driver instance
            _agent_session (AgentSession): stores properties of the current agent session
            _token (str): The development token used to authenticate with the Agent
            _reportsettings (ReportSettings): Settings (project name, job name) to be included in the report
            _sock (socket.Socket): Socket used in communicating with the Agent
            _queue (queue.Queue): queue holding reports to be sent to Agent in separate thread
    """

    REPORTS_QUEUE_TIMEOUT = 10

    def __init__(self, token: str, capabilities: dict, reportsettings: ReportSettings):
        self._remote_address = ConfigHelper.get_agent_service_address()
        self._capabilities = capabilities
        self._agent_session = None
        self._token = token
        self._reportsettings = reportsettings
        self._queue = queue.Queue()

        self._running = True
        self._reporting_thread = threading.Thread(target=self.__report_worker, daemon=True)
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

        self._agent_session = AgentSession(
            start_session_response.server_address,
            start_session_response.session_id,
            start_session_response.dialect,
            start_session_response.capabilities,
        )

        self._sock = SocketHelper.create_connection(self._remote_address, start_session_response.dev_socket_port)

        logging.info("Development session started...")
        return True

    def _request_session_from_agent(self) -> SessionResponse:
        """Creates and sends a session request object

            Returns:
                SessionResponse: object containing the response to the session request
        """
        session_request = SessionRequest(self._capabilities, self._reportsettings)

        logging.info(f"Session request: {session_request.to_json()}")

        try:
            response = self.send_request(
                "POST", f"{self._remote_address}{Endpoint.DevelopmentSession.value}", session_request.to_json(),
            )
        except requests.exceptions.ConnectionError:
            logging.error(f"Could not start new session on {self._remote_address}. Is your Agent running?")
            logging.error("You can download the TestProject Agent from https://app.testproject.io/#/agents")
            raise SdkException(f"Connection error trying to connect to Agent on {self._remote_address}")

        if not response.passed:
            self.__handle_new_session_error(response)

        start_session_response = SessionResponse(
            dev_socket_port=response.data["devSocketPort"],
            server_address=response.data["serverAddress"],
            session_id=response.data["sessionId"],
            dialect=response.data["dialect"],
            capabilities=response.data["capabilities"],
        )
        return start_session_response

    def send_request(self, method, path, body) -> OperationResult:
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
                response = session.post(path, headers={"Authorization": self._token}, json=body)
            elif method == "DELETE":
                response = session.delete(path, headers={"Authorization": self._token})
            else:
                raise SdkException(f"Unsupported HTTP method {method} in send_request()")

        try:
            response.raise_for_status()
            try:
                # For some successful calls, the response body will be empty
                # Parsing it results in a ValueError, so we should handle this
                response_json = response.json()
            except ValueError:
                response_json = {}
            return OperationResult(True, response.status_code, "", response_json)
        except HTTPError as http_error:
            return OperationResult(False, response.status_code, str(http_error), None)

    def send_action_execution_request(self, codeblock_guid: str, body: dict) -> ActionExecutionResponse:
        """Sends HTTP request to Agent

            Args:
                codeblock_guid (str): The codeblock GUID to be executed
                body (dict): Parameters to be passed to the Agent

            Returns:
                ActionExecutionResponse: contains result of the sent execution request
        """

        response = self.send_request("POST", f"{self._remote_address}{Endpoint.ActionExecution.value}/{codeblock_guid}", body,)

        if not response.passed:
            result = ExecutionResultType.Failed
        else:
            result = ExecutionResultType.Passed if response.data["resultType"] == "Passed" else ExecutionResultType.Failed

        result_data = response.data["outputs"] if response.passed else None

        return ActionExecutionResponse(result, response.message, result_data)

    def report_driver_command(self, driver_command_report: DriverCommandReport):
        """Sends command report to the Agent

        Args:
            driver_command_report: object containing the driver command to be reported
        """
        endpoint = f"{self._remote_address}{Endpoint.ReportDriverCommand.value}"

        queue_item = QueueItem(report_as_json=driver_command_report.to_json(), url=endpoint, token=self._token)

        self._queue.put(queue_item, block=False)

    def report_step(self, step_report: StepReport):
        """Sends step report to the Agent

        Args:
            step_report (StepReport): object containing the step to be reported
        """
        endpoint = f"{self._remote_address}{Endpoint.ReportStep.value}"

        queue_item = QueueItem(report_as_json=step_report.to_json(), url=endpoint, token=self._token)

        self._queue.put(queue_item, block=False)

    def report_test(self, test_report: CustomTestReport):
        """Sends test report to the Agent

        Args:
            test_report (CustomTestReport): object containing the test to be reported
        """
        endpoint = f"{self._remote_address}{Endpoint.ReportTest.value}"

        queue_item = QueueItem(report_as_json=test_report.to_json(), url=endpoint, token=self._token)

        self._queue.put(queue_item, block=False)

    def stop(self):
        """Send all remaining report items in the queue to TestProject"""
        # Send a stop signal to the thread worker
        self._running = False

        # Send a final, empty, report to the queue to ensure that
        # the 'running' condition is evaluated one last time
        self._queue.put(QueueItem(report_as_json=None, url=None, token=self._token), block=False)

        # Wait until all items have been reported or timeout passes
        self._reporting_thread.join(timeout=self.REPORTS_QUEUE_TIMEOUT)
        if self._reporting_thread.is_alive():
            # Thread is still alive, so there are unreported items
            logging.warning(f"There are {self._queue.qsize()} unreported items in the queue")

        try:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            logging.info(f"Connection to Agent at {self._remote_address} closed successfully")
        except socket.error as msg:
            logging.error(f"Failed to close socket connection to Agent at {self._remote_address}: {msg}")
            pass

    @staticmethod
    def __handle_new_session_error(response: OperationResult):
        """ Handles errors occurring on creation of a new session with the Agent

        Args:
            response (OperationResult): response from the Agent
        """
        if response.status_code == 401:
            logging.error("Invalid developer token supplied")
            logging.error(
                "Get your developer token from https://app.testproject.io/#/integrations/sdk?lang=Python"
                " and set it in the TP_DEV_TOKEN environment variable"
            )
            logging.error(f"Response from Agent: {response.message}")
            raise SdkException("Invalid developer token supplied")
        elif response.status_code == 406:
            logging.error(f"This SDK version ({ConfigHelper.get_sdk_version()}) is incompatible with your Agent version.")
            logging.error(f"Response from Agent: {response.message}")
            raise SdkException(f"Invalid SDK version {ConfigHelper.get_sdk_version()}")
        else:
            logging.error("Failed to initialize a session with the Agent")
            logging.error(f"Response from Agent: {response.message}")
            raise SdkException("Failed to initialize a session with the Agent")

    def __report_worker(self):
        """Worker method that is polling the queue for items to report"""
        while self._running or self._queue.qsize() > 0:

            item = self._queue.get()
            if isinstance(item, QueueItem):
                item.send()
            else:
                logging.warning(f"Unknown object of type {type(item)} found on queue, ignoring it..")
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
            response = session.post(self._url, headers={"Authorization": self._token}, json=self._report_as_json,)
            try:
                response.raise_for_status()
            except HTTPError:
                logging.error(f"Reporting to TestProject returned an HTTP {response.status_code}")
                logging.error(f"Response from Agent: {response.text}")


@unique
class Endpoint(Enum):
    DevelopmentSession = "/api/development/session"
    ActionExecution = "/api/codeblocks/executions"
    ReportDriverCommand = "/api/development/report/command"
    ReportStep = "/api/development/report/step"
    ReportTest = "/api/development/report/test"
    AddonExecution = "/api/addons/executions"
