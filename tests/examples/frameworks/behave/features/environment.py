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
from src.testproject.decorator.behave_reporter import behave_reporter

""" Executed once per test run: Before any features and scenarios are run.
    Initialize the driver and start the session.
"""


@behave_reporter()
def before_all(context):
    context.driver = webdriver.Chrome(project_name="Python BDD", job_name="Behave")


""" Executed after each step in the scenario.
    Reports the test step.
"""


@behave_reporter(screenshot=True)
def after_step(context, step):
    pass


""" Executed after each scenario in the feature.
    Reports the scenario as a test.
"""


@behave_reporter
def after_scenario(context, scenario):
    pass


""" Executed once per test run: after all features and scenarios are run.
    Quit the driver and close the session.
"""


def after_all(context):
    context.driver.quit()
