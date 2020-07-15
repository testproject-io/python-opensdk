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

from selenium.webdriver.remote.command import Command


class RedactHelper:
    """Class providing helper methods for command redaction

    Args:
        command_executor: The command executor used to send WebDriver commands (Selenium or Appium)

    Attributes:
        _command_executor: The command executor used to send WebDriver commands (Selenium or Appium)
    """

    def __init__(self, command_executor):
        self._command_executor = command_executor

    def redact_command(self, command: str, params: dict):
        """Redacts sensitive contents (passwords) so they do not appear in the reports

        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload

        Returns:
            dict: A redacted version of the dictionary, where password values are replaced by '****'
        """
        if (
                command == Command.SEND_KEYS_TO_ELEMENT
                or command == Command.SEND_KEYS_TO_ACTIVE_ELEMENT
        ):
            element_id = params["id"]

            if not self._redaction_required(element_id):
                return params

            # Change text typed into redactable field to '***'
            params["text"] = "***"
            params["value"] = list("***")

        return params

    def _redaction_required(self, element_id: str) -> bool:
        """Checks if the element should be redacted

        Args:
            element_id (str): The ID of the element under investigation

        Returns:
            bool: True if the element should be redacted, False otherwise
        """
        capabilities = self._command_executor.agent_client.agent_session.capabilities
        platform_name = capabilities.get("platformName")
        browser_name = capabilities.get("browserName")

        # Check if element is a mobile password element
        if platform_name.casefold() == "android":
            # Check that we're not dealing with mobile web
            if browser_name is None or browser_name == "":
                return self._is_android_password_element(element_id)

        return self._is_secured_element(element_id)

    def _is_android_password_element(self, element_id: str) -> bool:
        """Checks if the element is an Android password element

        Args:
            element_id (str): The ID of the element under investigation

        Returns:
            bool: True if the element is an Android password element, False otherwise
        """
        get_attribute_params = {
            "sessionId": self._command_executor.agent_client.agent_session.session_id,
            "id": element_id,
            "name": "password",
        }
        get_attribute_response = self._command_executor.execute(
            Command.GET_ELEMENT_ATTRIBUTE, get_attribute_params, True
        )

        return get_attribute_response.get("value").casefold() == "true"

    def _is_secured_element(self, element_id: str) -> bool:
        """Checks if the element is a secured element (an HTML or iOS password element)

        Args:
            element_id (str): The ID of the element under investigation

        Returns:
            bool: True if the element is a secured element, False otherwise
        """
        get_attribute_params = {
            "sessionId": self._command_executor.agent_client.agent_session.session_id,
            "id": element_id,
            "name": "type",
        }
        get_attribute_response = self._command_executor.execute(
            Command.GET_ELEMENT_ATTRIBUTE, get_attribute_params, True
        )
        return get_attribute_response["value"] in ["password", "XCUIElementTypeSecureTextField"]
