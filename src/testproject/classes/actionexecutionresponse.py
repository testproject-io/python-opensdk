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
from src.testproject.enums import ExecutionResultType


class ActionExecutionResponse:
    def __init__(
        self, executionresulttype: ExecutionResultType = ExecutionResultType.NoResult, message: str = "", outputs: dict = None,
    ):
        self._executionresulttype = executionresulttype
        self._message = message
        self._outputs = outputs

    @property
    def executionresulttype(self) -> ExecutionResultType:
        return self._executionresulttype

    @executionresulttype.setter
    def executionresulttype(self, value: ExecutionResultType):
        self._executionresulttype = value

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str):
        self._message = value

    @property
    def outputs(self) -> dict:
        return self._outputs

    @outputs.setter
    def outputs(self, value: dict):
        self._outputs = value
