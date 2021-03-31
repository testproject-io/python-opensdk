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

from selenium.webdriver.common.by import By

from src.testproject.classes import ElementSearchCriteria
from src.testproject.enums import ExecutionResultType, FindByType
from src.testproject.rest.messages import AddonExecutionResponse
from src.testproject.sdk.addons import ActionProxy
from src.testproject.sdk.exceptions import SdkException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import ReportingCommandExecutor
from src.testproject.sdk.internal.reporter import Reporter


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

        # Objects for handling any StepSettings
        settings = self._command_executor.settings
        step_helper = self._command_executor.step_helper

        # Handling driver timeout
        step_helper.handle_timeout(settings.timeout)
        # Handling sleep before execution
        step_helper.handle_sleep(sleep_timing_type=settings.sleep_timing_type, sleep_time=settings.sleep_time)

        # Execute the action
        response: AddonExecutionResponse = self._agent_client.execute_proxy(action)

        # Handling sleep after execution
        step_helper.handle_sleep(
            sleep_timing_type=settings.sleep_timing_type,
            sleep_time=settings.sleep_time,
            step_executed=True,
        )

        if response.execution_result_type is not ExecutionResultType.Passed and not settings.invert_result:
            raise SdkException(f"Error occurred during addon action execution: {response.message}")

        # Update attributes value from response
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

        # Extract result from response result.
        result = True if response.execution_result_type is ExecutionResultType.Passed else False
        result, step_message = step_helper.handle_step_result(
            step_result=result,
            base_msg=response.message,
            invert_result=settings.invert_result,
            always_pass=settings.always_pass,
        )

        # Handle screenshot condition
        screenshot = step_helper.take_screenshot(settings.screenshot_condition, result)

        # Getting the addon name from its proxy descriptor class name.
        # For example:
        #   action.proxydescriptor.classname = io.testproject.something.i.dont.care.TypeRandomPhoneNumber
        #   description is 'Execute TypeRandomPhoneNumber'.
        description = f'Execute \'{action.proxydescriptor.classname.split(".")[-1]}\''

        element = None
        # If proxy descriptor has the by property and the by property is implemented by TestProject's FindByType...
        if action.proxydescriptor.by and FindByType.has_value(action.proxydescriptor.by):
            element = ElementSearchCriteria(
                find_by_type=FindByType(action.proxydescriptor.by),
                by_value=action.proxydescriptor.by_value,
                index=-1,
            )
        # Creating input/output fields
        input_fields = {f.name: f.value for f in response.fields if not f.is_output}
        output_fields = {f.name: f.value for f in response.fields if f.is_output}
        # Manually reporting the addon step with all the information.
        Reporter(command_executor=self._command_executor).step(
            description=description,
            message=f"{step_message}{os.linesep}",
            element=element,
            inputs=input_fields,
            outputs=output_fields,
            passed=result,
            screenshot=screenshot,
        )
        return action
