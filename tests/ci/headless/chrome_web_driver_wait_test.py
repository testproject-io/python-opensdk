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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from src.testproject.classes import WebDriverWait, DriverStepSettings, StepSettings
from src.testproject.enums import TakeScreenshotConditionType
from selenium.webdriver.support import expected_conditions as ec
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import ChromeOptions

from tests.pageobjects.web import LoginPage, ProfilePage


@pytest.fixture
def driver():
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    driver = webdriver.Chrome(chrome_options=chrome_options, project_name="CI - Python")
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
