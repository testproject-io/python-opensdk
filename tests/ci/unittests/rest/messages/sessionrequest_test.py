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

from src.testproject.helpers import ConfigHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages import SessionRequest


def test_sessionrequest_to_json(mocker):
    # mock the response to get_sdk_version() as this will change over time
    mocker.patch.object(ConfigHelper, "get_sdk_version")
    ConfigHelper.get_sdk_version.return_value = "1.2.3.4"

    capabilities = {"key": "value"}
    reportsettings = ReportSettings("my_project", "my_job")
    session_request = SessionRequest(capabilities, reportsettings)
    assert session_request.to_json() == {
        "projectName": "my_project",
        "jobName": "my_job",
        "capabilities": {"key": "value"},
        "sdkVersion": "1.2.3.4",
        "language": "Python",
    }
