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
    driver = webdriver.Safari(project_name="Examples", job_name=None)
    yield driver
    driver.quit()


def test_example_using_safari(driver):

    LoginPage(driver).open().login_as("John Smith", "12345")
    assert ProfilePage(driver).greetings_are_displayed() is True
