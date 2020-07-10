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
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


class LoginPage:

    url = "https://example.testproject.io/web/"

    textfield_name = (By.CSS_SELECTOR, "#name")
    textfield_password = (By.CSS_SELECTOR, "#password")
    button_dologin = (By.CSS_SELECTOR, "#login")

    def __init__(self, driver: BaseDriver):
        self._driver = driver

    def open(self):
        self._driver.get(self.url)
        return self

    def login_as(self, username: str, password: str):
        self._driver.find_element(*self.textfield_name).send_keys(username)
        self._driver.find_element(*self.textfield_password).send_keys(password)
        self._driver.find_element(*self.button_dologin).click()
