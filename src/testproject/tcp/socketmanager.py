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
import socket
import select

from src.testproject.sdk.exceptions import AgentConnectException


class SocketManager:
    """Class used to manage the development TCP socket connection.

    Attributes:
        __instance (SocketManager): The singleton instance of this class
    """

    __instance = None

    __socket = None

    # Timeout for validation between the socket and the Agent in seconds.
    _SOCKET_VALIDATION_TIMEOUT = 15

    @classmethod
    def instance(cls):
        """Return the singleton instance of the SocketManager class"""
        if cls.__instance is None:
            cls.__instance = SocketManager()
        return cls.__instance

    def close_socket(self):
        """Close the connection to the Agent development socket"""
        if self.is_connected():
            try:
                SocketManager.__socket.shutdown(socket.SHUT_RDWR)
                SocketManager.__socket.close()
                SocketManager.__socket = None
                logging.info("Connection to Agent closed successfully")
            except socket.error as msg:
                logging.error(f"Failed to close socket connection to Agent: {msg}")

    def open_socket(self, socket_address: str, socket_port: int, uuid: str):
        """Opens a connection to the Agent development socket

        Args:
            socket_address (str): The address for the socket
            socket_port (int): The development socket port to connect to
            agent_version (str): The current agent version in use
            uuid (str): The returned UUID from the agent
        """

        if SocketManager.__socket is not None:
            logging.debug("open_socket(): Socket already exists")
            return

        if self.is_connected():
            logging.debug("open_socket(): Socket is already connected")
            return

        SocketManager.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SocketManager.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        SocketManager.__socket.connect((socket_address, socket_port))

        if not self.is_connected():
            raise AgentConnectException("Failed connecting to Agent socket")

        # Validate connection to the Agent by waiting for a message starting from Agent 2.3.0.
        # Only agent 2.3.0 or greater will return a none empty UUID.
        if uuid:
            logging.debug("Validating connection to the Agent...")
            connected = False

            # Check the agent responded with the correct UUID in both socket and agent response
            # within the given timeout of 15 seconds
            ready = select.select([SocketManager.__socket], [], [], self._SOCKET_VALIDATION_TIMEOUT)
            if ready[0]:
                # The response is in ASCII, convert it to string
                # Take only from the 2nd index as the first 2 bytes represent a header
                message = SocketManager.__socket.recv(36).decode()[2:]
                if message == uuid:
                    connected = True

            if not connected:
                raise AgentConnectException(
                    f"SDK failed to connect to the Agent via a TCP socket on port {socket_port}.\n"
                    + "Please check if you have any interfering software installed, and disable it."
                )

        logging.info(f"Socket connection to {socket_address}:{socket_port} established successfully")

    @staticmethod
    def is_connected() -> bool:
        """Sends a simple message to the socket to see if it's connected

        Returns:
            bool: True if the socket is connected, False otherwise
        """
        if SocketManager.__socket is None:
            return False

        try:
            SocketManager.__socket.send("test".encode("utf-8"))
            return True
        except socket.error as msg:
            logging.warning(f"Socket not connected: {msg}")
            return False
