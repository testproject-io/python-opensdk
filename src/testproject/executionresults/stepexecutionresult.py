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
from src.testproject.executionresults.executionresult import ExecutionResult


class StepExecutionResult(ExecutionResult):
    def __init__(self):
        super().__init__()
        self._assertions = None
        self._conditions = None
        self._description: str = ""
        # TODO: implement other properties of class StepExecutionResult

    @property
    def assertions(self):
        return self._assertions

    @assertions.setter
    def assertions(self, value):
        self._assertions = value

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        self._conditions = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
