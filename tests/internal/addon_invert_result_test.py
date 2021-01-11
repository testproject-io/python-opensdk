import pytest
from selenium.webdriver.common.by import By

from proxy_examples.actions import TypeRandomPhoneAction
from src.testproject.classes import DriverStepSettings, StepSettings
from src.testproject.decorator import report
from src.testproject.sdk.drivers import webdriver

DEV_TOKEN = "kjvgLv5jxNuy5g48Nd2BMrOFG-kGdaZ86goeBjhsqts1"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(token=DEV_TOKEN, projectname="Addon Invert Result Project",
                              jobname="Addon Invert Result Job")
    yield driver
    driver.quit()


@report(test="Addon Invert Result Test")
def test_report_decorator(driver):
    driver.get("https://example.testproject.io/web/")

    driver.find_element_by_css_selector("#name").send_keys("John Smith")
    driver.find_element_by_css_selector("#password").send_keys("12345")
    driver.find_element_by_css_selector("#login").click()

    textfield_phone = (By.CSS_SELECTOR, "#phone")
    # The TypeRandomPhoneAction addon generates a unique phone number
    # and types that in the specified textfield
    # Inverting result using the StepSettings.
    with DriverStepSettings(driver, StepSettings(invert_result=True)):
        driver.addons().execute(TypeRandomPhoneAction("1", 10), *textfield_phone)
