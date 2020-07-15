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
from src.testproject.sdk.drivers.actions import Actions
from src.testproject.sdk.internal.agent import AgentClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.testproject.sdk.drivers.actions.action_guids import driver_actions


class DriverActions(Actions):
    """Offers methods to execute driver actions

    Args:
        agent_client (AgentClient): client to communicate with the Agent
        timeout (int): timeout for action execution
    """

    def __init__(self, agent_client: AgentClient, timeout: int):
        super().__init__(agent_client, timeout)

    def send_keys_to_window(self, keys) -> bool:
        """Send a list of keystrokes to the current browser

        Args:
            keys: list of keystrokes

        Returns:
            bool: True if the action was performed successfully, False otherwise
        """
        typable_keys = self.__convert_to_typable(keys)
        body = {"text": ",".join(typable_keys)}
        response = self.action_execute(driver_actions["SEND_KEYS_ID"], body, None, "")
        return response.executionresulttype == ExecutionResultType.Passed

    def is_selected(self, by: By, by_value: str) -> bool:
        """Checks if an element is selected

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element is selected, False otherwise
        """
        response = self.action_execute(driver_actions["IS_SELECTED_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def is_present(self, by: By, by_value: str) -> bool:
        """Checks if an element is present in the DOM

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element is present in the DOM, False otherwise
        """
        response = self.action_execute(driver_actions["IS_PRESENT_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def is_visible(self, by: By, by_value: str) -> bool:
        """Checks if an element is visible

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element is visible, False otherwise
        """
        response = self.action_execute(driver_actions["IS_VISIBLE_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def contains_text(self, text_to_find: str, by: By, by_value: str) -> bool:
        """Checks if the text of an element contains a given substring

        Args:
            text_to_find (str): The substring to find in the element text
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element text contains the given substring, False otherwise
        """
        body = {"text": text_to_find}
        response = self.action_execute(driver_actions["CONTAINS_TEXT_ID"], body, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def is_clickable(self, by: By, by_value: str) -> bool:
        """Checks if an element is clickable

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element is clickable, False otherwise
        """
        response = self.action_execute(driver_actions["IS_CLICKABLE_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def is_invisible(self, by: By, by_value: str) -> bool:
        """Checks if an element is invisible (or not present in the DOM)

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if the element is invisible, False otherwise
        """
        response = self.action_execute(driver_actions["IS_INVISIBLE_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def send_keys(self, text_to_type: str, by: By, by_value: str) -> bool:
        """Sends the given text to the specified element

        Args:
            text_to_type (str): The text to type in the element
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: Element text if the action was successful, None otherwise
        """
        body = {"keys": text_to_type}
        response = self.action_execute(driver_actions["TYPE_TEXT_ID"], body, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def clear_contents(self, by: By, by_value: str) -> bool:
        """Clears the contents of an element

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: Element text if the element was found, None otherwise
        """
        response = self.action_execute(driver_actions["CLEAR_CONTENTS_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def get_text(self, by: By, by_value: str) -> str:
        """Retrieves the visible text of an element

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: Element text if the element was found, None otherwise
        """
        response = self.action_execute(driver_actions["GET_TEXT_ID"], {}, by, by_value)
        if response.executionresulttype != ExecutionResultType.Passed:
            return None
        return response.outputs["text"]

    def click(self, by: By, by_value: str) -> bool:
        """Clicks an element

        Args:
            by (By): Selenium locator strategy (By.ID, By.NAME, ...)
            by_value (str): The associated value for the locator strategy

        Returns:
            bool: True if action was performed successfully, False otherwise
        """
        response = self.action_execute(driver_actions["CLICK_ID"], {}, by, by_value)
        return response.executionresulttype == ExecutionResultType.Passed

    def get_title(self) -> str:
        """Retrieves the current driver or application title

        Returns:
            bool: Driver or application title if successful, None otherwise
        """
        response = self.action_execute(driver_actions["GET_TITLE_ID"], {})
        if response.executionresulttype != ExecutionResultType.Passed:
            return None
        return response.outputs["title"]

    @staticmethod
    def __convert_to_typable(keys):
        """Converts a list of characters to a typable representation

        Returns:
            list: typable version of the list of characters
        """
        typing = []
        for key in keys:
            if isinstance(key, Keys):
                typing.append(key)
            elif isinstance(key, int):
                key = str(key)
                for i in range(len(key)):
                    typing.append(key[i])
            else:
                for i in range(len(key)):
                    typing.append(key[i])
        return typing
