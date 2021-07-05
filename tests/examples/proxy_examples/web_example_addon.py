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
from src.testproject.sdk.drivers import webdriver
from tests.examples.proxy_examples.actions import TypeRandomPhoneAction, ClearFieldsAction
from tests.pageobjects.web import LoginPage, ProfilePage

PASSWORD = "12345"
WRONG_PASSWORD = "54321"
FULL_NAME = "John Smith"


def example_test_with_addon():
    driver = webdriver.Chrome()

    # Login using provided credentials
    LoginPage(driver).open().login_as(FULL_NAME, WRONG_PASSWORD)

    # Use Addon proxy to invoke 'Clear Fields' Action
    driver.addons().execute(ClearFieldsAction())

    # Login using correct credentials
    LoginPage(driver).open().login_as(FULL_NAME, PASSWORD)

    # Complete profile form with an empty phone number
    ProfilePage(driver).update_profile(
        country="Canada",
        address="Maple Street 456",
        email="bob@jones.org",
        phone="",
    )

    # Use Addon proxy to invoke 'Type Random Phone' Action
    # Notice how the action parameters are provided using an action proxy convenience method
    driver.addons().execute(TypeRandomPhoneAction("1", 10), by=By.CSS_SELECTOR, by_value="#phone")

    # Save the profile form
    ProfilePage(driver).save()

    # Check if saved label is present
    driver.report().step("Profile completed", ProfilePage(driver).is_saved(), True)


if __name__ == "__main__":
    example_test_with_addon()
