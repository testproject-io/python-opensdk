import pytest

from src.testproject.decorator import report
from src.testproject.sdk.drivers import webdriver

DEV_TOKEN = "Hnw-B_FakRKt5Nar7jICIbHNTwBNW9Pp09MH_nXZTI41"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(token=DEV_TOKEN, project_name="Report Decorator Project", job_name="Report Decorator Job")
    yield driver
    driver.quit()


@report(test="Report Decorator Test")
def test_report_decorator(driver):
    driver.get(url="https://www.google.com")
