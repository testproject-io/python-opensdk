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
            projectname (str): Project name to report
            jobname (str): Job name to report

        Attributes:
            _projectname (str): Project name to report
            _jobname (str): Job name to report
    """

    def __init__(self, projectname: str, jobname: str):
        self._projectname = projectname
        self._jobname = jobname

    @property
    def projectname(self):
        """Getter for the project name"""
        return self._projectname

    @property
    def jobname(self):
        """Getter for the job name"""
        return self._jobname

    def __eq__(self, other):
        """Custom equality function"""
        if not isinstance(other, ReportSettings):
            return NotImplemented

        return (
            self._projectname == other._projectname and self._jobname == other._jobname
        )

    def __hash__(self):
        """Implement hash to allow objects to be used in sets and dicts"""
        return hash((self._projectname, self._jobname))
