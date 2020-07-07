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
