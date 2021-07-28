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

import os
import logging

from src.testproject import definitions


class ConfigHelper:
    """Contains helper methods for SDK configuration"""

    @staticmethod
    def get_agent_service_address() -> str:
        """Returns the Agent service address as defined in the TP_AGENT_URL environment variable.
            Defaults to http://127.0.0.1:8585 (localhost)

        Returns:
            str: the Agent service address
        """
        address = os.getenv("TP_AGENT_URL")
        if address is None:
            logging.info(
                "No Agent service address found in TP_AGENT_URL environment variable, "
                "defaulting to http://127.0.0.1:8585 (localhost)"
            )
            address = "http://127.0.0.1:8585"
        else:
            # Replace 'localhost' with '127.0.0.1' to prevent delays as a result of DNS lookups
            # Since we support remote execution, the address variable does not have to hold localhost or
            # 127.0.0.1 in it's value
            address = address.replace("localhost", "127.0.0.1")
        logging.info(f"Using {address} as the Agent URL")
        return address

    @staticmethod
    def get_developer_token() -> str:
        """Returns the TestProject developer token as defined in the TP_DEV_TOKEN environment variable

        Returns:
            str: the developer token
        """
        return os.getenv("TP_DEV_TOKEN")

    @staticmethod
    def get_sdk_version() -> str:
        """Returns the SDK version as defined in the definitions module

        Returns:
            str: the current SDK version
        """
        return definitions.get_sdk_version()
