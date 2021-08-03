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

import queue
import threading
import logging
from src.testproject.tcp import SocketManager
from typing import Optional
import requests
from requests import HTTPError


class ReportsQueue:
    REPORTS_QUEUE_TIMEOUT = 10

    def __init__(self, token: str):
        self._token = token
        self._close_socket = False
        # Running after all is initialized successfully
        self._running = True
        # After session started and is running, start the reporting thread
        self._queue = queue.Queue()
        self._reporting_thread = threading.Thread(target=self._report_worker, daemon=True)
        self._reporting_thread.start()

    def submit(self, report_as_json: [dict], url: [str], block: [bool]):
        queue_item = QueueItem(
            report_as_json=report_as_json,
            url=url,
            token=self._token,
        )
        self._queue.put(queue_item, block=block)

    def stop(self):
        """Send all remaining report items in the queue to TestProject"""
        # Send a stop signal to the thread worker
        self._running = False

        # Send a final, empty, report to the queue to ensure that
        # the 'running' condition is evaluated one last time
        self._queue.put(QueueItem(report_as_json=None, url=None, token=self._token), block=False)

        # Wait until all items have been reported or timeout passes
        self._reporting_thread.join(timeout=self.REPORTS_QUEUE_TIMEOUT)
        if self._reporting_thread.is_alive():
            # Thread is still alive, so there are unreported items
            logging.warning(f"There are {self._queue.qsize()} unreported items in the queue")

    def _report_worker(self):
        """Worker method that is polling the queue for items to report"""
        while self._running or self._queue.qsize() > 0:
            item = self._queue.get()
            if isinstance(item, QueueItem):
                self._handle_report(item)
            else:
                logging.warning(f"Unknown object of type {type(item)} found on queue, ignoring it..")
            self._queue.task_done()
        # Close socket only after agent_client is no longer running and all reports in the queue have been sent.
        if self._close_socket:
            SocketManager.instance().close_socket()

    def _handle_report(self, item: [object]):
        item.send()


class QueueItem:
    """Helper class representing an item to be reported

    Args:
        report_as_json (dict): JSON payload representing the item to be reported
        url (str): Agent endpoint the payload should be POSTed to
        token (str): Token used to authenticate with the Agent

    Attributes:
        _report_as_json (Optional[dict]): JSON payload representing the item to be reported
        _url (Optional[str]): Agent endpoint the payload should be POSTed to
        _token (str): Token used to authenticate with the Agent
    """

    def __init__(self, report_as_json: Optional[dict], url: Optional[str], token: str):
        self._report_as_json = report_as_json
        self._url = url
        self._token = token

    def send(self):
        """Send a report item to the Agent"""
        max_report_failure_attempts = 4

        if self._report_as_json is None and self._url is None:
            # Skip empty queue items put in the queue on stop()
            return

        for i in range(max_report_failure_attempts):
            with requests.Session() as session:
                response = session.post(
                    self._url,
                    headers={"Authorization": self._token},
                    json=self._report_as_json,
                )
                try:
                    response.raise_for_status()
                    return
                except HTTPError:
                    remaining_attempts = max_report_failure_attempts - i - 1
                    logging.warning(
                        f"Agent responded with an unexpected status {response.status_code}, "
                        f"response from Agent: {response.text}"
                    )
                    logging.info(f"Failed to send a report to the Agent, {remaining_attempts} attempts remaining...")
        logging.error(f"All {max_report_failure_attempts} attempts to send report have failed.")

    @property
    def report_as_json(self):
        return self._report_as_json
