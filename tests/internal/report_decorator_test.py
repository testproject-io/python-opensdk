import pytest

from src.testproject.decorator import report
from src.testproject.sdk.drivers import webdriver

DEV_TOKEN = "Hnw-B_FakRKt5Nar7jICIbHNTwBNW9Pp09MH_nXZTI41"


@pytest.fixture
def driver():
    def _driver():
        return webdriver.Chrome(token=DEV_TOKEN, projectname="Report Decorator Project", jobname="Report Decorator Job")
    driver = _driver()
    yield driver
    driver.quit()


# MAIN TEST #
@report(test="Report Decorator Test")
def test_report_decorator(driver):
    driver.get(url='https://www.google.com')
