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

from enum import Enum, unique


@unique
class EnvironmentVariable(Enum):
    """Enumeration of environment variable names used in the SDK"""

    TP_TEST_NAME = "TP_TEST_NAME"
    TP_PROJECT_NAME = "TP_PROJECT_NAME"
    TP_JOB_NAME = "TP_JOB_NAME"
    TP_DISABLE_AUTO_REPORTING = "TP_DISABLE_AUTO_REPORTING"

    def remove(self):
        """Try and remove the environment variable, proceed if the variable doesn't exist"""
        try:
            os.environ.pop(self.value)
        except KeyError:
            pass
