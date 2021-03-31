import pytest
from selenium.common.exceptions import TimeoutException

from src.testproject.classes import DriverStepSettings, StepSettings, WebDriverWait
from src.testproject.enums import TakeScreenshotConditionType
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from tests.pageobjects.web import LoginPage, ProfilePage

DEV_TOKEN = "ZNXf2v22_eXli4w4UsLM5ulkfxLHK1IqNSfHH7i2wyI1"


@pytest.fixture
def driver():
    driver = webdriver.Chrome(
        token=DEV_TOKEN, project_name="Web Driver Report Project", job_name="Web Driver Report Job"
    )
    yield driver
    driver.quit()


@pytest.fixture()
def wait(driver):
    wait = WebDriverWait(driver, 2)  # Notice the imports, using WebDriverWait from 'src.testproject.classes'
    yield wait


def test_wait_with_ec_invisible(driver, wait):
    # Case 1 - Should report passed.
    LoginPage(driver).open().login_as("John Smith", "12345")
    # Check successful login.
    assert ProfilePage(driver).greetings_are_displayed() is True
    ProfilePage(driver).logout()
    # Greeting label shouldn't be shown anymore after logout.
    textlabel_greetings = (By.CSS_SELECTOR, "#greetings")
    element_not_present = wait.until(ec.invisibility_of_element_located(textlabel_greetings))
    assert element_not_present
    # Case 2 - Should report failed.
    try:
        wait.until(ec.title_is("Title that is definitely not this one."))
    except TimeoutException:
        pass
    # Case 3 - Report with StepSettings
    # Inverting result and taking picture on success.
    # Wait should timeout and report fail which will be inverted to passed and include picture.
    with DriverStepSettings(
        driver=wait.driver,
        step_settings=StepSettings(invert_result=True, screenshot_condition=TakeScreenshotConditionType.Failure),
    ):
        try:
            wait.until_not(ec.url_contains("TestProject"))
        except TimeoutException:
            pass
