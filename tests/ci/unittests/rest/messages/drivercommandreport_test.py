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

import pytest

from src.testproject.rest.messages import DriverCommandReport


@pytest.fixture
def dcr():
    return DriverCommandReport(
        command="command",
        command_params={"param": "value"},
        result={"result": "value"},
        passed=True,
    )


@pytest.fixture
def dcr_with_screenshot():
    return DriverCommandReport(
        command="command",
        command_params={"param": "value"},
        result={"result": "value"},
        passed=False,
        screenshot="base64_screenshot",
    )


def test_instances_with_same_arguments_are_considered_equal(dcr):

    another_dcr = DriverCommandReport(
        command="command",
        command_params={"param": "value"},
        result={"result": "value"},
        passed=True,
    )

    assert another_dcr is not dcr
    assert another_dcr == dcr


def test_instances_with_different_arguments_are_considered_not_equal(dcr):

    another_dcr = DriverCommandReport(
        command="command",
        command_params={"param": "value"},
        result={"result": "another_value"},
        passed=True,
    )

    assert another_dcr is not dcr
    assert another_dcr != dcr


def test_to_json(dcr):
    assert dcr.to_json() == {
        "commandName": "command",
        "commandParameters": {"param": "value"},
        "result": {"result": "value"},
        "passed": True,
    }


def test_to_json_with_screenshot(dcr_with_screenshot):
    assert dcr_with_screenshot.to_json() == {
        "commandName": "command",
        "commandParameters": {"param": "value"},
        "result": {"result": "value"},
        "passed": False,
        "screenshot": "base64_screenshot",
    }
