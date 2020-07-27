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

import os
import pytest

from src.testproject.enums import ReportNamingElement
from src.testproject.helpers import ReportHelper


def test_test_name_is_inferred_correctly_from_method_name():
    assert (
        ReportHelper.infer_test_name()
        == "test_test_name_is_inferred_correctly_from_method_name"
    )


def test_project_name_is_inferred_correctly():
    assert ReportHelper.infer_project_name() == "tests.ci.unittests.helpers"


def test_job_name_is_inferred_correctly():
    assert ReportHelper.infer_job_name() == "reporthelper_test"


@pytest.mark.parametrize("parameter", ["panda", "polar bear", "african wild dog"])
def test_test_name_is_inferred_correctly_from_method_name_and_parameter_values(
    parameter,
):
    current_test_info = os.environ.get("PYTEST_CURRENT_TEST")
    assert (
        ReportHelper.infer_name_from_pytest_info_for(
            current_test_info, ReportNamingElement.Test
        )
        == f"test_test_name_is_inferred_correctly_from_method_name_and_parameter_values[{parameter}]"
    )
