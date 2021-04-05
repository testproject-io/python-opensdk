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

from src.testproject.sdk.drivers import webdriver
from src.testproject.decorator.pytestBDD_reporter import pytestBDD_reporter
import pytest

""" Executed after each succesful step in the scenario.
    Reports the test step.
"""


@pytest.fixture(scope="class")
def browser():
    driver = webdriver.Chrome(project_name="Python BDD", job_name="Python BDD")
    yield driver
    driver.quit


""" Executed after each succesful step in the scenario.
    Reports the test step.
"""


@pytestBDD_reporter(screenshot=True)
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    pass


""" Executed after each scenario in the feature.
    Reports the scenario as a test.
"""


@pytestBDD_reporter
def pytest_bdd_after_scenario(request, feature, scenario):
    pass


""" Executed once per test run: after all features and scenarios are run.
    Quit the driver and close the session.
"""


@pytestBDD_reporter
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    pass


@pytestBDD_reporter
def pytest_bdd_before_scenario(request, feature, scenario):
    pass
