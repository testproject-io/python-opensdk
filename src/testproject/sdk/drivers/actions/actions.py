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

from src.testproject.classes import ActionExecutionResponse
from src.testproject.enums import ExecutionResultType
from src.testproject.helpers import SeleniumHelper
from src.testproject.sdk.internal.agent import AgentClient
from selenium.webdriver.common.by import By
from src.testproject.sdk.drivers.actions.action_guids import actions


class Actions:
    """Offers method to execute all actions

    Args:
        agent_client (AgentClient): client to communicate with the Agent
        timeout (int): timeout for action execution

    Attributes:
        _agent_client (AgentClient): client to communicate with the Agent
        _timeout (int): timeout for action execution
    """

    def __init__(self, agent_client: AgentClient, timeout: int):
        self._agent_client = agent_client
        self._timeout = timeout

    def action_execute(
        self,
        action_guid: str,
        body: dict,
        by: By = None,
        by_value: str = "",
        timeout: int = 10000,
    ) -> ActionExecutionResponse:
        """Sends HTTP request to Agent

        Args:
            action_guid (str): The TestProject action GUID to be executed
            body (dict): Parameters to be passed to the Agent
            by (By): The locator strategy to be used to locate the element to perform the action on/with
            by_value (str): The associated locator strategy value
            timeout (int): timeout (in seconds) for the action execution

        Returns:
            ActionExecutionResponse: contains result of the sent execution request
        """
        body["_timeout"] = timeout

        if by is not None:
            search_criteria = SeleniumHelper.create_search_criteria(by, by_value)
            if search_criteria is not None:
                body["elementSearchCriteria"] = search_criteria.to_json()
            else:
                logging.error(f"Failure in creating search criteria from locator strategy {by} with value {by_value}")

        response = self._agent_client.send_action_execution_request(action_guid, body)
        if response.executionresulttype == ExecutionResultType.Failed:
            logging.warning(
                f"Failed to execute action '{inspect.stack()[1].function}', "
                "agent returned the following message: {response.message}"
            )
        return response

    def pause(self, milliseconds: int) -> bool:
        """Pause test execution for the specified duration

        Args:
            milliseconds (int): Number of milliseconds to pause test execution for

        Returns:
            bool: True if the action was performed successfully, False otherwise
        """
        body = {"milliseconds": milliseconds}
        response = self.action_execute(actions["PAUSE_ID"], body)
        return response.executionresulttype == ExecutionResultType.Passed
