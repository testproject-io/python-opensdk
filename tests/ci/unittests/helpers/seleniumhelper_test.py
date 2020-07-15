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

import pytest

from selenium.webdriver.common.by import By
from src.testproject.enums import FindByType
from src.testproject.helpers import SeleniumHelper
from src.testproject.sdk.exceptions import SdkException


def test_valid_search_criteria_yields_elementsearchcriteria():
    esc = SeleniumHelper.create_search_criteria(By.CSS_SELECTOR, "#css")
    assert esc.find_by_type == FindByType.CSSSELECTOR
    assert esc.by_value == "#css"
    assert esc.index == -1


def test_invalid_search_criteria_raises_exception():
    with pytest.raises(SdkException) as sdke:
        SeleniumHelper.create_search_criteria(None, "empty")
    assert str(sdke.value) == "Did not recognize locator strategy None"
