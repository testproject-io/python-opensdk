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

from src.testproject.sdk.drivers import webdriver
from tests.pageobjects.web import LoginPage, ProfilePage


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    # disable all automatic reports, tests and steps will be reported manually
    driver.report().disable_auto_test_reports(disabled=True)
    yield driver
    driver.quit()


def test_is_reported_as_passed(driver):

    LoginPage(driver).open().login_as("John Smith", "12345")
    assert ProfilePage(driver).greetings_are_displayed() is True
    driver.report().test(name="Passing test", passed=True)


def test_is_reported_as_failed_with_additional_step(driver):
    LoginPage(driver).open().login_as("John Smith", "12345")
    assert ProfilePage(driver).greetings_are_displayed() is True
    driver.report().step(
        description="Failing step with screenshot",
        message="An additional message that goes with the step",
        passed=False,
        screenshot=True,
    )
    driver.report().test(name="Failing test", passed=False)
