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

from src.testproject.sdk.exceptions.notimplementedexception import (
    NotImplementedException,
)
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers.reporting_command_executor import (
    ReportingCommandExecutor,
)


class GenericCommandExecutor(ReportingCommandExecutor):
    """Custom command executor class for the generic driver

    Args:
        agent_client (AgentClient): Client used to communicate with the TestProject Agent
    """

    def __init__(self, agent_client: AgentClient):
        ReportingCommandExecutor.__init__(self, agent_client=agent_client, command_executor=self,
                                          remote_connection=None)

    def execute(self, command: str, params: dict, skip_reporting: bool = False):
        """Not implemented for generic driver objects

        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload
            skip_reporting (bool): True if command should not be reported to Agent, False otherwise
        """
        raise NotImplementedException("Not implemented for generic driver")
