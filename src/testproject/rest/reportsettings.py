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

from src.testproject.enums.report_type import ReportType


class ReportSettings:
    """Contains settings to be used in the report.

    Args:
        project_name (str): Project name to report
        job_name (str): Job name to report
        report_type (Optional[ReportType]): Report type = cloud, local or both.

    Attributes:
        _project_name (str): Project name to report
        _job_name (str): Job name to report
        _report_type (ReportType): Report type = cloud, local or both.
    """

    def __init__(
        self,
        project_name: str,
        job_name: str,
        report_type: ReportType = ReportType.CLOUD_AND_LOCAL,
        report_name: str = None,
        report_path: str = None,
    ):
        self._project_name = project_name
        self._job_name = job_name
        self._report_type = report_type
        self._report_name = report_name
        self._report_path = report_path

    @property
    def project_name(self) -> str:
        """Getter for the project name"""
        return self._project_name

    @property
    def job_name(self) -> str:
        """Getter for the job name"""
        return self._job_name

    @property
    def report_type(self) -> ReportType:
        """Getter for the report type"""
        return self._report_type

    @property
    def report_name(self) -> str:
        """Getter for the report type"""
        return self._report_name

    @property
    def report_path(self) -> str:
        """Getter for the report type"""
        return self._report_path

    def __eq__(self, other):
        """Custom equality function"""
        if not isinstance(other, ReportSettings):
            return NotImplemented

        return (
            self.project_name == other.project_name
            and self.job_name == other.job_name
            and self.report_type == other.report_type
        )

    def __hash__(self):
        """Implement hash to allow objects to be used in sets and dicts"""
        return hash((self._project_name, self._job_name, self._report_type))
