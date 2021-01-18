import pytest
from selenium.common.exceptions import TimeoutException

from src.testproject.classes import DriverStepSettings, StepSettings, WebDriverWait
from src.testproject.enums import TakeScreenshotConditionType
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

DEV_TOKEN = "ZNXf2v22_eXli4w4UsLM5ulkfxLHK1IqNSfHH7i2wyI1"


@pytest.fixture
def browser():
    driver = webdriver.Chrome(token=DEV_TOKEN, project_name="Web Driver Report Project",
                              job_name="Web Driver Report Job")
    yield driver
    driver.quit()


@pytest.fixture()
def wait(browser):
    wait = WebDriverWait(browser, 2)
    yield wait


def test_wait_with_ec_invisible(browser, wait):
    # Case 1 - Should report passed.
    browser.get('http://www.google.com')
    search_field = (By.CSS_SELECTOR, "input[name='z']")  # => z should be q, thus simulating a non-present element
    element_not_present = wait.until(ec.invisibility_of_element_located(search_field))
    assert element_not_present
    # Case 2 - Should report failed.
    try:
        wait.until(ec.title_is("Title that is definitely not this one."))
    except TimeoutException:
        pass
    # Case 3 - Report with StepSettings
    # Inverting result and taking picture on success.
    # Wait should timeout and report fail which will be inverted to passed and include picture.
    with DriverStepSettings(driver=wait.driver,
                            step_settings=StepSettings(invert_result=True,
                                                       screenshot_condition=TakeScreenshotConditionType.Failure)):
        try:
            wait.until_not(ec.url_contains("google"))
        except TimeoutException:
            pass
