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

import unittest

from src.testproject.decorator import report
from src.testproject.sdk.drivers import webdriver
from tests.pageobjects.web import LoginPage, ProfilePage


class TestBasic(unittest.TestCase):
    @report(
        project="Examples",
        job="unittest example",
        test="Basic flow on TestProject demo app",
    )
    def test_login_to_testproject_demo_app(self):
        driver = webdriver.Chrome()
        LoginPage(driver).open().login_as("John Smith", "12345")
        assert ProfilePage(driver).greetings_are_displayed() is True
        driver.quit()


if __name__ == "__main__":
    unittest.main()
