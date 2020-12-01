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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from proxy_examples.actions import TypeRandomPhoneAction
from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import ChromeOptions


@pytest.fixture
def driver():
    chrome_options = ChromeOptions()
    chrome_options.headless = True
    driver = webdriver.Chrome(chrome_options=chrome_options, projectname="CI - Python")
    yield driver
    driver.quit()


def test_update_profile_using_addon_proxy_expect_success_message_to_be_displayed(driver):

    textfield_phone = (By.CSS_SELECTOR, "#phone")

    driver.get("https://example.testproject.io/web/")

    driver.find_element_by_css_selector("#name").send_keys("John Smith")
    driver.find_element_by_css_selector("#password").send_keys("12345")
    driver.find_element_by_css_selector("#login").click()

    Select(driver.find_element_by_css_selector("#country")).select_by_visible_text("Australia")
    driver.find_element_by_css_selector("#address").send_keys("Main Street 123")
    driver.find_element_by_css_selector("#email").send_keys("john@smith.org")

    # The TypeRandomPhoneAction addon generates a unique phone number
    # and types that in the specified textfield
    driver.addons().execute(TypeRandomPhoneAction("1", 10), *textfield_phone)

    driver.find_element_by_css_selector("#save").click()

    assert driver.find_element_by_css_selector("#saved").is_displayed()
