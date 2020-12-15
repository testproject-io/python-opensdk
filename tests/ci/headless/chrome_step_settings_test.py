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
from time import time

import pytest

from src.testproject.classes import StepSettings, DriverStepSettings
from src.testproject.enums import TakeScreenshotConditionType, SleepTimingType
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import ChromeOptions
from tests.pageobjects.web import LoginPage


@pytest.fixture
def driver():
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    driver = webdriver.Chrome(chrome_options=chrome_options, projectname="CI - Python")
    yield driver
    driver.quit()


def test_basic_login_with_step_settings(driver):
    step_settings = StepSettings(timeout=15000, screenshot_condition=TakeScreenshotConditionType.Success,
                                 sleep_timing_type=SleepTimingType.Before, sleep_time=1000)
    start_time = time()
    with DriverStepSettings(driver, step_settings):
        LoginPage(driver).open().login_as("John Smith", "12345")  # Has about 7 driver commands.
    end_time = time()
    assert end_time - start_time >= 7.0
