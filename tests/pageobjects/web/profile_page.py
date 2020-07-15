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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


class ProfilePage:

    textlabel_greetings = (By.CSS_SELECTOR, "#greetings")
    textlabel_saved = (By.CSS_SELECTOR, "#saved")
    dropdown_country = (By.CSS_SELECTOR, "#country")
    textfield_address = (By.CSS_SELECTOR, "#address")
    textfield_email = (By.CSS_SELECTOR, "#email")
    textfield_phone = (By.CSS_SELECTOR, "#phone")
    button_save = (By.CSS_SELECTOR, "#save")
    button_logout = (By.CSS_SELECTOR, "#logout")

    def __init__(self, driver: BaseDriver):
        self._driver = driver

    def greetings_are_displayed(self):
        return self._driver.find_element(*self.textlabel_greetings).is_displayed()

    def saved_message_is_displayed(self):
        return self._driver.find_element(*self.textlabel_saved).is_displayed()

    def update_profile(self, country: str, address: str, email: str, phone: str):
        Select(self._driver.find_element(*self.dropdown_country)).select_by_visible_text(country)
        self._driver.find_element(*self.textfield_address).send_keys(address)
        self._driver.find_element(*self.textfield_email).send_keys(email)
        self._driver.find_element(*self.textfield_phone).send_keys(phone)
        self._driver.find_element(*self.button_save).click()

    def logout(self):
        self._driver.find_element(*self.button_logout).click()
