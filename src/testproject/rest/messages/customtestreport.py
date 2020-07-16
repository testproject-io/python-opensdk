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


class CustomTestReport:
    """Payload object sent to the Agent when reporting a test.

    Args:
        name (str): The test name
        passed (bool): True if the test should be marked as passed, False otherwise
        message (str): A message that goes with the test

    Attributes:
        _name (str): The test name
        _passed (bool): True if the test should be marked as passed, False otherwise
        _message (str): A message that goes with the test
    """

    def __init__(self, name: str, passed: bool, message: str = None):
        self._name = name
        self._passed = passed
        self._message = message

    @property
    def name(self):
        """Getter for the name property"""
        return self._name

    @name.setter
    def name(self, value):
        """Setter for the name property"""
        self._name = value

    @property
    def passed(self):
        """Getter for the passed property"""
        return self._passed

    @passed.setter
    def passed(self, value):
        """Setter for the passed property"""
        self._passed = value

    @property
    def message(self):
        """Getter for the message property"""
        return self._message

    @message.setter
    def message(self, value):
        """Setter for the message property"""
        self._message = value

    def to_json(self):
        """Generates a dict containing the JSON representation of the test payload"""
        return {"name": self._name, "passed": self._passed, "message": self._message}
