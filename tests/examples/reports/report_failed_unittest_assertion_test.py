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

from selenium.webdriver import ChromeOptions
from src.testproject.decorator import report_assertion_errors
from src.testproject.sdk.drivers import webdriver
from tests.pageobjects.web import LoginPage


class TestBasic(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(
            chrome_options=ChromeOptions(), projectname="Examples", jobname=None
        )

    @report_assertion_errors
    def test_auto_report_failed_unittest_assertion(self):
        LoginPage(self.driver).open().login_as("John Smith", "12345")
        self.assertEqual(
            self.driver.title,
            "Incorrect Title"
        )  # This assertion fails and will be reported

    def tearDown(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
