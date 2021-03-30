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

from src.testproject.enums import SleepTimingType, TakeScreenshotConditionType


class StepSettings:
    """Represents settings for automatic step reporting.

    Args:
        sleep_time: is the sleep time number in milliseconds.
        sleep_timing_type: defines if the sleep will occur 'Before' or 'After' step execution.
        timeout: of the driver AKA explicit wait.
        invert_result: will invert step execution result when True.
        always_pass: will forcefully pass the step in case of failure when True.

    Examples:
        # This class should be used with a driver.
        # Option 1 - assuming driver instance 'driver'
        driver.step_settings = StepSettings(**args)
        # Option 2 - using the DriverStepSettings
        with DriverStepSettings(driver, StepSettings(**args)):
            # Some driver command.

    """

    def __init__(
        self,
        sleep_time: int = 0,
        sleep_timing_type: SleepTimingType = None,
        timeout: int = -1,
        invert_result: bool = False,
        always_pass: bool = False,
        screenshot_condition: TakeScreenshotConditionType = TakeScreenshotConditionType.Failure,
    ):
        self.sleep_time = sleep_time
        self.sleep_timing_type = sleep_timing_type
        self.timeout = timeout
        self.always_pass = always_pass
        self.invert_result = invert_result
        self.screenshot_condition = screenshot_condition
