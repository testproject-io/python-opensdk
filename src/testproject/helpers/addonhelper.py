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

from selenium.webdriver.common.by import By

from src.testproject.enums import ExecutionResultType
from src.testproject.rest.messages import AddonExecutionResponse
from src.testproject.sdk.addons import ActionProxy
from src.testproject.sdk.exceptions import SdkException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import ReportingCommandExecutor


class AddonHelper:
    def __init__(self, agent_client: AgentClient, command_executor: ReportingCommandExecutor):
        self._agent_client = agent_client
        self._command_executor = command_executor

    def execute(self, action: ActionProxy, by: By = None, by_value: str = None) -> ActionProxy:

        # Set the locator properties
        action.proxydescriptor.by = by
        action.proxydescriptor.by_value = by_value

        # Set the list of parameters for the action
        for param in action.__dict__:
            # Skip the _proxydescriptor attribute itself
            if param not in ["_proxydescriptor"]:
                action.proxydescriptor.parameters[param] = action.__dict__[param]

        response: AddonExecutionResponse = self._agent_client.execute_proxy(action)
        if response.executionresulttype != ExecutionResultType.Passed:
            raise SdkException(f"Error occurred during addon action execution: {response.message}")

        for field in response.fields:

            # skip non-output fields
            if not field.is_output:
                continue

            # check if action has an attribute with the name of the field
            if not hasattr(action, field.name):
                logging.warning(f"Action '{action.proxydescriptor.guid}' does not have a field named '{field.name}'")
                continue

            # update the attribute value with the value from the response
            setattr(action, field.name, field.value)

        return action
