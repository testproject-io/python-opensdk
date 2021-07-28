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

from src.testproject.rest.messages.reportitemtype import ReportItemType
import uuid

from src.testproject.classes import ElementSearchCriteria


class StepReport:
    """Payload object sent to the Agent when reporting a test step.

    Args:
        description (str): The step description
        message (str): A message that goes with the step
        passed (bool): True if the step should be marked as passed, False otherwise
        screenshot (str): A base64 encoded screenshot that is associated with the step
        element (ElementSearchCriteria): The step's element search criteria.
        inputs (dict): Dictionary of step input parameters - name:value
        outputs (dict): Dictionary of step output parameters - name:value

    Attributes:
        _description (str): The step description
        _message (str): A message that goes with the step
        _passed (bool): True if the step should be marked as passed, False otherwise
        _screenshot (str): A base64 encoded screenshot that is associated with the step
        _element (dict): The step's element search criteria in JSON representation.
        _input_params (dict): Dictionary of step input parameters - name:value
        _output_params (dict): Dictionary of step output parameters - name:value
    """

    def __init__(
        self,
        description: str,
        message: str,
        passed: bool,
        screenshot: str = None,
        element: ElementSearchCriteria = None,
        inputs: dict = None,
        outputs: dict = None,
    ):
        self._description = description
        self._message = message
        self._passed = passed
        self._screenshot = screenshot
        self._element = element.to_json() if element else None
        self._input_params = inputs
        self._output_params = outputs

    def to_json(self) -> dict:
        """Generates a dict containing the JSON representation of the step payload"""
        json = {
            "guid": str(uuid.uuid4()),
            "description": self._description,
            "message": self._message,
            "passed": self._passed,
            "element": self._element,
            "screenshot": self._screenshot,
            "inputParameters": self._input_params,
            "outputParameters": self._output_params,
            "type": ReportItemType.Step.value,
        }

        return json
