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
import logging
from time import sleep

from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.remote_connection import RemoteConnection

from src.testproject.enums import SleepTimingType


class StepHelper:

    def __init__(self, executor: RemoteConnection, w3c: bool):
        self.executor = executor
        self.w3c = w3c

    def handle_timeout(self, timeout, session_id):
        if timeout > 0:
            logging.debug(f'Setting driver implicit wait to {timeout} milliseconds.')
            if self.w3c:
                self.executor.execute(Command.SET_TIMEOUTS, {'sessionId': session_id, 'implicit': int(timeout)})
            else:
                self.executor.execute(Command.IMPLICIT_WAIT, {'sessionId': session_id, 'ms': float(timeout)})

    def handle_sleep(self, sleep_timing_type, sleep_time, command, step_executed=False):
        # Sleep Before if not Quit command
        if command is not Command.QUIT:
            if sleep_timing_type:
                sleep_timing_type_condition = SleepTimingType.After if step_executed else SleepTimingType.Before
                if sleep_timing_type is sleep_timing_type_condition:
                    logging.debug(f'Step is designed to sleep for {sleep_time} milliseconds'
                                  f' {sleep_timing_type.name} execution.')
                    sleep(sleep_time / 1000.0)
