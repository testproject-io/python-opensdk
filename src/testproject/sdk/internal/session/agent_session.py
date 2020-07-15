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


class AgentSession:
    """Object representing the current Agent session

    Args:
        remote_address (str): The Agent address
        session_id (str): A unique identifier for the current Agent session
        dialect (str): The WebDriver dialect associated with the session (W3C or OSS)
        capabilities (str): driver-specific capabilities

    Attributes:
        _remote_address (str): The Agent address
        _session_id (str): A unique identifier for the current Agent session
        _dialect (str): The WebDriver dialect associated with the session (W3C or OSS)
        _capabilities (str): driver-specific capabilities
    """

    def __init__(self, remote_address: str, session_id: str, dialect: str, capabilities: dict):
        self._remote_address = remote_address
        self._session_id = session_id
        self._dialect = dialect
        self._capabilities = capabilities

    @property
    def remote_address(self) -> str:
        """Getter for the Agent address"""
        return self._remote_address

    @property
    def session_id(self) -> str:
        """Getter for the current session ID"""
        return self._session_id

    @property
    def dialect(self) -> str:
        """Getter for the session dialect"""
        return self._dialect

    @property
    def capabilities(self) -> dict:
        """Getter for the driver capabilities"""
        return self._capabilities
