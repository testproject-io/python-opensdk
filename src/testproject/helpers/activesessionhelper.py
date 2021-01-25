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

from src.testproject.sdk.drivers.webdriver import Remote, Generic
from src.testproject.sdk.drivers.webdriver.base import BaseDriver
from src.testproject.sdk.exceptions import SdkException


def get_active_driver_instance():
    """Get the current driver instance in use (BaseDriver, Remote or Generic) """
    # Get the first driver instance that exists (not None) in the list of possible driver instances.
    driver = next((_driver for _driver in [BaseDriver.instance(), Remote.instance(), Generic.instance()] if _driver
                  is not None), None)
    if driver is None:
        raise SdkException("No active driver instance found for reporting")
    return driver
