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
from selenium.webdriver.common.by import By

from src.testproject.classes import ElementSearchCriteria
from src.testproject.enums import FindByType

from src.testproject.sdk.exceptions import SdkException


class SeleniumHelper:
    @staticmethod
    def create_search_criteria(by: By, by_value: str):
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
        else:
            raise SdkException(f"Did not recognize locator strategy {by}")

    @staticmethod
    def create_addon_locator(by: By, by_value: str):
        if by == By.ID:
            return {"id": by_value}
        elif by == By.NAME:
            return {"name": by_value}
        elif by == By.XPATH:
            return {"xpath", by_value}
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
        else:
            raise SdkException(f"Did not recognize locator strategy {by}")
