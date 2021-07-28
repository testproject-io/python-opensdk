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


from src.testproject.rest.messages.reportitemtype import ReportItemType


class DriverCommandReport:
    """Payload object sent to the Agent when reporting a driver command.

    Args:
        command (str): The name of the command that was executed
        command_params (dict): Parameters associated with the command
        result (dict): The result of the command that was executed
        passed (bool): Indication whether or not command execution was performed successfully
        screenshot (str): Screenshot as base64 encoded string
        message (str): The message to include in the result

    Attributes:
        _command (str): The name of the command that was executed
        _command_params (dict): Parameters associated with the command
        _result (dict): The result of the command that was executed
        _passed (bool): Indication whether or not command execution was performed successfully
        _screenshot (str): Screenshot as base64 encoded string
        _message (str): The message to include in the result
    """

    def __init__(
        self,
        command: str,
        command_params: dict,
        result: dict,
        passed: bool,
        screenshot: str = None,
        message: str = None,
    ):
        self._command = command
        self._command_params = command_params
        self._result = result
        self._passed = passed
        self._screenshot = screenshot
        self._message = message

    @property
    def command(self) -> str:
        """Getter for the command property"""
        return self._command

    @property
    def command_params(self) -> dict:
        """Getter for the command_params property"""
        return self._command_params

    @property
    def result(self) -> dict:
        """Getter for the result property"""
        return self._result

    @property
    def passed(self) -> bool:
        """Getter for the passed property"""
        return self._passed

    @property
    def screenshot(self) -> str:
        """Getter for the screenshot property"""
        return self._screenshot

    @screenshot.setter
    def screenshot(self, value: str):
        """Setter for the screenshot property"""
        self._screenshot = value

    @property
    def message(self) -> str:
        """Getter for the message property"""
        return self._message

    @message.setter
    def message(self, value: str):
        """Setter for the message property"""
        self._message = value

    def to_json(self):
        """Creates a JSON representation of the current DriverCommandReport instance

        Returns:
            dict: JSON representation of the current instance
        """
        payload = {
            "commandName": self.command,
            "commandParameters": self.command_params,
            "result": self.result,
            "passed": self.passed,
            "message": self.message,
            "screenshot": self.screenshot,
            "type": ReportItemType.Command.value,
        }

        return payload

    def __eq__(self, other):
        """Custom equality function, used in report stashing"""
        if not isinstance(other, DriverCommandReport):
            return NotImplemented

        return (
            self._command == other._command
            and self.command_params == other.command_params
            and self.result == other.result
            and self.passed == other.passed
            and self.message == other.message
            and self.screenshot == other.screenshot
        )

    def __hash__(self):
        """Implement hash to allow objects to be used in sets and dicts"""
        return hash(
            (
                self.command,
                self.command_params,
                self.result,
                self.passed,
                self.screenshot,
                self.message,
            )
        )
