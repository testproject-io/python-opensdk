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

from appium.webdriver.common.mobileby import MobileBy
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


class LoginPage:

    textfield_name = (MobileBy.ID, "name")
    textfield_password = (MobileBy.ID, "password")
    button_dologin = (MobileBy.ID, "login")

    def __init__(self, driver: BaseDriver):
        self._driver = driver

    def login_as(self, username: str, password: str):
        self._driver.find_element(*self.textfield_name).send_keys(username)
        self._driver.find_element(*self.textfield_password).send_keys(password)
        self._driver.find_element(*self.button_dologin).click()
