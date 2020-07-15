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


class SessionRequest:
    """Represent a request message object to be sent to the Agent to initialize a new session

    Args:
        capabilities (dict): Desired session capabilities
        reportsettings (ReportSettings): Settings to be used in the report

    Attributes:
        _capabilities (dict): Desired session capabilities
        _sdk_version (str): Current Python SDK version
        _language (str): Test code language (Python, obviously)
        _projectname (str): Project name to report
        _jobname (str): Job name to report
    """

    def __init__(self, capabilities: dict, reportsettings: ReportSettings):
        self._capabilities: dict = capabilities
        self._sdk_version = ConfigHelper.get_sdk_version()
        self._language = "Python"
        self._projectname = reportsettings.projectname
        self._jobname = reportsettings.jobname

    def to_json(self):
        """Returns a JSON representation of the current SessionRequest instance"""
        return {
            "projectName": self._projectname,
            "jobName": self._jobname,
            "capabilities": self._capabilities,
            "sdkVersion": self._sdk_version,
            "language": self._language,
        }
