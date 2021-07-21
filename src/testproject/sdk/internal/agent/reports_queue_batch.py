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
import collections
import logging
import os
from src.testproject.sdk.internal.agent.reports_queue import ReportsQueue, QueueItem


class ReportsQueueBatch(ReportsQueue):
    MAX_REPORT_BATCH_SIZE = 10
    TP_MAX_BATCH_SIZE_VARIABLE_NAME = "TP_MAX_REPORTS_BATCH_SIZE"

    def __init__(self, token: str, url: [str]):
        super().__init__(token)
        self._url = url
        self.__batch_list = collections.deque()
        """Get maximum reports batch size from environment variable."""
        """If the environment variable is not defined - set maximum reports batch size to 10 as default"""
        try:
            env_var_value = os.environ[self.TP_MAX_BATCH_SIZE_VARIABLE_NAME]
            if env_var_value is not None:
                self.__max_batch_size = int(env_var_value)
            else:
                self.__max_batch_size = self.MAX_REPORT_BATCH_SIZE
        except KeyError:
            logging.warning("The environment variable {TP_MAX_BATCH_SIZE_VARIABLE_NAME} is not defined.")
            self.__max_batch_size = self.MAX_REPORT_BATCH_SIZE
        except ValueError:
            logging.warning("The environment variable {TP_MAX_BATCH_SIZE_VARIABLE_NAME} value must be an integer.")
            self.__max_batch_size = self.MAX_REPORT_BATCH_SIZE
        except Exception:
            self.__max_batch_size = self.MAX_REPORT_BATCH_SIZE
        logging.info("The maximum reports batch size is defined as {self.__max_batch_size}.")

    def _handle_report(self, item: [object]):
        self.__batch_list.append(item.report_as_json)

        if self.__batch_list.__len__() == 0:
            return

        """Send the reports batch, if one of the following conditions is true:"""
        """The batch list size reached allowed maximum."""
        """The queue is empty and the reports batch list is not."""
        if self.__batch_list.__len__() == self.__max_batch_size or (
            self.__batch_list.__len__() > 0 and self._queue.qsize() == 0
        ):
            """Convert reports linked list to a plain list before it's sent to the Agent"""
            batch_json = list(self.__batch_list)
            """Build QueueItem with reports batch json and send it to the agent"""
            batch_item = QueueItem(url=self._url, report_as_json=batch_json, token=self._token)
            batch_item.send()
            self.__batch_list.clear()
