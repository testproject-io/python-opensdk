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
        report_settings (ReportSettings): Settings to be used in the report

    Attributes:
        _capabilities (dict): Desired session capabilities
        _sdk_version (str): Current Python SDK version
        _language (str): Test code language (Python, obviously)
        _project_name (str): Project name to report
        _job_name (str): Job name to report
        _report_type (ReportType): Report type = cloud, local or both.
        _report_name (str): The name of the generated report.
        _report_path (str): The path of the generated report.
    """

    def __init__(self, capabilities: dict, report_settings: ReportSettings):
        self._capabilities: dict = capabilities
        self._sdk_version = ConfigHelper.get_sdk_version()
        self._language = "Python"
        self._project_name = report_settings.project_name
        self._job_name = report_settings.job_name
        self._report_type = report_settings.report_type
        self._report_name = report_settings.report_name
        self._report_path = report_settings.report_path

    def to_json(self):
        """Returns a JSON representation of the current SessionRequest instance"""
        return {
            "projectName": self._project_name,
            "jobName": self._job_name,
            "capabilities": self._capabilities,
            "sdkVersion": self._sdk_version,
            "language": self._language,
            "reportType": self._report_type.name,
            "reportName": self._report_name,
            "reportPath": self._report_path,
        }
