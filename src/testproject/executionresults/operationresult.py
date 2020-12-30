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
from typing import Optional


class OperationResult:
    """Represents the result of an operation performed by the Agent

    Args:
        passed (bool): True if the operation was executed successfully, False otherwise
        status_code (int): The HTTP status code of the Agent response
        message (str): A message returned by the Agent after the operation execution
        data (Optional[dict]): Output data for the operation performed

    Attributes:
        _passed (bool): True if the operation was executed successfully, False otherwise
        _status_code (int): The HTTP status code of the Agent response
        _message (str): A message returned by the Agent after the operation execution
        _data (Optional[dict]): Output data for the operation performed

    """
    def __init__(self, passed: bool = False, status_code: int = 500, message: str = "", data: Optional[dict] = None):
        self._passed = passed
        self._status_code = status_code
        self._message = message
        self._data = data

    @property
    def passed(self):
        """Getter for the pass / fail indication"""
        return self._passed

    @passed.setter
    def passed(self, value):
        """Setter for the pass / fail indication"""
        self._passed = value

    @property
    def status_code(self):
        """Getter for the response status code"""
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        """Setter for the response status code"""
        self._status_code = value

    @property
    def message(self):
        """Getter for the operation response message"""
        return self._message

    @message.setter
    def message(self, value):
        """Setter for the operation response message"""
        self._message = value

    @property
    def data(self):
        """Getter for the operation output data"""
        return self._data

    @data.setter
    def data(self, value):
        """Setter for the operation output data"""
        self._data = value
