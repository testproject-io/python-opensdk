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

import uuid

from src.testproject.enums import ExecutionResultType, ExecutionFailureType


class ExecutionResult:
    """Represent the result of the execution of an action

    Attributes:
        _guid: An UUID uniquely identifying the executed action
        _resulttype (ExecutionResultType): The execution result type
        _failuretype (ExecutionFailureType): The execution failure type
        _message (str): A message returned by the Agent upon the action execution
    """
    def __init__(self):
        self._guid = uuid.uuid4()
        self._resulttype: ExecutionResultType = ExecutionResultType.NoResult
        self._failuretype: ExecutionFailureType = ExecutionFailureType.NoFailure
        self._message: str = ""

    @property
    def guid(self):
        """Getter for the action guid"""
        return self._guid

    @guid.setter
    def guid(self, value):
        """Setter for the action guid"""
        self._guid = value

    @property
    def resulttype(self):
        """Getter for the action execution result type"""
        return self._resulttype

    @resulttype.setter
    def resulttype(self, value):
        """Setter for the action execution result type"""
        self._resulttype = value

    @property
    def failuretype(self):
        """Getter for the action execution failure type"""
        return self._failuretype

    @failuretype.setter
    def failuretype(self, value):
        """Setter for the action execution failure type"""
        self._failuretype = value

    @property
    def message(self):
        """Getter for the action execution result message"""
        return self._message

    @message.setter
    def message(self, value):
        """Setter for the action execution result message"""
        self._message = value
