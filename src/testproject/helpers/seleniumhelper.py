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

from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from src.testproject.classes import ElementSearchCriteria
from src.testproject.enums import FindByType
from src.testproject.sdk.exceptions import SdkException


class SeleniumHelper:
    """Contains helper methods for Selenium actions, mostly locator-related"""

    @staticmethod
    def create_search_criteria(by: By, by_value: str):
        """Translator method to create element search criteria to send to the Agent

        Args:
            by (By): The element locator strategy to be used
            by_value (str): The associated element locator strategy value

        Returns:
            ElementSearchCriteria: object representing the element search criteria
        """

        if by == By.ID:
            return ElementSearchCriteria(FindByType.ID, by_value)
        elif by == By.NAME:
            return ElementSearchCriteria(FindByType.NAME, by_value)
        elif by == By.XPATH:
            return ElementSearchCriteria(FindByType.XPATH, by_value)
        elif by == By.CLASS_NAME:
            return ElementSearchCriteria(FindByType.CLASSNAME, by_value)
        elif by == By.CSS_SELECTOR:
            return ElementSearchCriteria(FindByType.CSSSELECTOR, by_value)
        elif by == By.LINK_TEXT:
            return ElementSearchCriteria(FindByType.LINKTEXT, by_value)
        elif by == By.PARTIAL_LINK_TEXT:
            return ElementSearchCriteria(FindByType.PARTIALLINKTEXT, by_value)
        elif by == By.TAG_NAME:
            return ElementSearchCriteria(FindByType.TAG_NAME, by_value)
        elif by == MobileBy.ACCESSIBILITY_ID:
            return ElementSearchCriteria(FindByType.ACCESSIBILITYID, by_value)
        elif by == MobileBy.IOS_PREDICATE:
            return ElementSearchCriteria(FindByType.IOSPREDICATE, by_value)
        else:
            raise SdkException(f"Did not recognize locator strategy {by}")

    @staticmethod
    def create_addon_locator(by: By, by_value: str) -> dict:
        """Creates and returns an locator used in an addon based on a locator strategy

        Args:
            by (By): The element locator strategy to be used
            by_value (str): The associated element locator strategy value

        Returns:
            dict: object representing the element locator strategy to use in the addon
        """

        if by == By.ID:
            return {"id": by_value}
        elif by == By.NAME:
            return {"name": by_value}
        elif by == By.XPATH:
            return {"xpath": by_value}
        elif by == By.CLASS_NAME:
            return {"className": by_value}
        elif by == By.CSS_SELECTOR:
            return {"cssSelector": by_value}
        elif by == By.LINK_TEXT:
            return {"linkText": by_value}
        elif by == By.PARTIAL_LINK_TEXT:
            return {"partialLinkText": by_value}
        elif by == By.TAG_NAME:
            return {"tagName": by_value}
        elif by == MobileBy.ACCESSIBILITY_ID:
            return {"accessibilityId": by_value}
        elif by == MobileBy.IOS_PREDICATE:
            return {"iosPredicate": by_value}
        else:
            raise SdkException(f"Did not recognize locator strategy {by}")
