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
    return DriverCommandReport("command", {"param": "value"}, {"result": "value"}, True)


def test_instances_with_same_arguments_are_considered_equal(dcr):

    another_dcr = DriverCommandReport("command", {"param": "value"}, {"result": "value"}, True)

    assert another_dcr is not dcr
    assert another_dcr == dcr


def test_instances_with_different_arguments_are_considered_not_equal(dcr):

    another_dcr = DriverCommandReport("command", {"param": "value"}, {"result": "another_value"}, True)

    assert another_dcr is not dcr
    assert another_dcr != dcr


def test_to_json(dcr):
    assert dcr.to_json() == {
        "commandName": "command",
        "commandParameters": {"param": "value"},
        "result": {"result": "value"},
        "passed": True,
    }
