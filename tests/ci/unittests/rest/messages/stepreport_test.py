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

import uuid

from src.testproject.rest.messages import StepReport


def test_to_json_without_screenshot(mocker):
    # mock the response to uuid4() as this will change each time
    mocker.patch.object(uuid, "uuid4")
    uuid.uuid4.return_value = "12-ab-34-cd"

    step_report = StepReport(description="my_description", message="my_message", passed=True)
    assert step_report.to_json() == {
        "guid": "12-ab-34-cd",
        "description": "my_description",
        "message": "my_message",
        "passed": True,
    }


def test_to_json_with_screenshot(mocker):
    # mock the response to uuid4() as this will change each time
    mocker.patch.object(uuid, "uuid4")
    uuid.uuid4.return_value = "56-ef-78-gh"

    step_report = StepReport(
        description="another_description", message="another_message", passed=False, screenshot="base64_screenshot_here",
    )
    assert step_report.to_json() == {
        "guid": "56-ef-78-gh",
        "description": "another_description",
        "message": "another_message",
        "passed": False,
        "screenshot": "base64_screenshot_here",
    }
