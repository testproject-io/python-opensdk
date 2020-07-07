from src.testproject.classes import ElementSearchCriteria
from src.testproject.enums import FindByType


def test_to_json_with_default_arguments():
    esc_json = ElementSearchCriteria(FindByType.XPATH, "//xpath").to_json()
    assert esc_json == {"byType": "XPATH", "byValue": "//xpath", "index": -1}


def test_to_json_with_custom_arguments():
    esc_json = ElementSearchCriteria(FindByType.CSSSELECTOR, "#cssselector", 5).to_json()
    assert esc_json == {"byType": "CSSSELECTOR", "byValue": "#cssselector", "index": 5}
