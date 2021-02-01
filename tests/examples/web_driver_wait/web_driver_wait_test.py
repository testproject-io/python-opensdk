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

# Notice we import WebDriverWait from SDK classes!
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from src.testproject.classes import WebDriverWait
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver.support import expected_conditions as ec

from tests.pageobjects.web import LoginPage, ProfilePage


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture()
def wait(driver):
    wait = WebDriverWait(driver, 2)  # Notice the imports, using WebDriverWait from 'src.testproject.classes'
    yield wait


def test_wait_with_ec_invisible(driver, wait):
    # Driver command will fail because element will not be found but this is the expected result so this step actually
    # passes and will reported as passed as well.
    LoginPage(driver).open().login_as("John Smith", "12345")
    # Check successful login.
    assert ProfilePage(driver).greetings_are_displayed() is True
    ProfilePage(driver).logout()
    # Greeting label shouldn't be shown anymore after logout.
    textlabel_greetings = (By.CSS_SELECTOR, "#greetings")
    element_not_present = wait.until(ec.invisibility_of_element_located(textlabel_greetings))
    assert element_not_present
    # This step will fail because the example page's title is not the one we give below, step will be reported as failed
    # and a TimeoutException will arose by the WebDriverWait instance.
    try:
        wait.until(ec.title_is("Title that is definitely not this one."))
    except TimeoutException:
        pass
