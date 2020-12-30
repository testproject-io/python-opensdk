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


class ReportSettings:
    """Contains settings to be used in the report.

        Args:
            project_name (str): Project name to report
            job_name (str): Job name to report

        Attributes:
            _project_name (str): Project name to report
            _job_name (str): Job name to report
    """

    def __init__(self, project_name: str, job_name: str):
        self._project_name = project_name
        self._job_name = job_name

    @property
    def project_name(self) -> str:
        """Getter for the project name"""
        return self._project_name

    @property
    def job_name(self) -> str:
        """Getter for the job name"""
        return self._job_name

    def __eq__(self, other):
        """Custom equality function"""
        if not isinstance(other, ReportSettings):
            return NotImplemented

        return self._project_name == other._project_name and self._job_name == other._job_name

    def __hash__(self):
        """Implement hash to allow objects to be used in sets and dicts"""
        return hash((self._project_name, self._job_name))
