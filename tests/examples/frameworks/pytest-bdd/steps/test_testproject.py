# Copyright 2021 TestProject (https://testproject.io)
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

from pytest_bdd import scenario, given, when, then


@scenario("../features/selenium_test.feature", "Run a Simple BDD test with TestProject")
def test_testproject():
    pass


@given("I navigate to the TestProject example page")
def step_impl_given(browser):
    browser.get("https://example.testproject.io/web/")


@when("I perform a login")
def step_impl_when(browser):
    browser.find_element_by_css_selector("#name").send_keys("John Smith")
    browser.find_element_by_css_selector("#password").send_keys("12345")
    browser.find_element_by_css_selector("#login").click()


@then("I should see a logout button")
def step_impl_then(browser):
    passed = browser.find_element_by_css_selector("#logout").is_displayed()
    assert passed is True
