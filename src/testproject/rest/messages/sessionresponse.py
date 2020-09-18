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


class SessionResponse:
    """Represent a response message object returned by the Agent when initializing a new session

    Args:
        dev_socket_port (int): The developer socket port
        server_address (str): The Agent address
        session_id (str): Unique identifier for the current development session
        dialect (str): Indicates the WebDriver dialect (W3C or OSS)
        capabilities (dict): Desired session capabilities
        agent_version (str): Agent version, required to check backwards compatibility

    Attributes:
        _dev_socket_port (int): The developer socket port
        _server_address (str): The Agent address
        _session_id (str): Unique identifier for the current development session
        _dialect (str): Indicates the WebDriver dialect (W3C or OSS)
        _capabilities (dict): Desired session capabilities
        _agent_version (str): Agent version, required to check backwards compatibility
    """

    def __init__(
        self,
        dev_socket_port: int,
        server_address: str,
        session_id: str,
        dialect: str,
        capabilities: dict,
        agent_version: str,
    ):
        self._dev_socket_port = dev_socket_port
        self._server_address = server_address
        self._session_id = session_id
        self._dialect = dialect
        self._capabilities = capabilities
        self._agent_version = agent_version

    @property
    def dev_socket_port(self) -> int:
        """Getter for the development socket port number"""
        return self._dev_socket_port

    @property
    def server_address(self) -> str:
        """Getter for the Agent address"""
        return self._server_address

    @property
    def session_id(self) -> str:
        """Getter for the unique session ID"""
        return self._session_id

    @property
    def dialect(self):
        """Getter for the WebDriver dialect in use"""
        return self._dialect

    @property
    def capabilities(self) -> dict:
        """Getter for the driver session capabilities"""
        return self._capabilities

    @property
    def agent_version(self) -> str:
        """Getter for the Agent version"""
        return self._agent_version
