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
from urllib.parse import urlparse

from src.testproject.sdk.exceptions import SdkException


class SocketHelper:
    @staticmethod
    def create_connection(socket_address: str, socket_port: int) -> socket:
        """Parses the agent service address and attempts to create a socket connection

            Args:
                socket_address (str): The address for the socket
                socket_port (int): The development socket port to connect to

            Returns:
                socket: Socket object that has been created and connected to
        """
        host = urlparse(socket_address).hostname

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.connect((host, socket_port))

        if not SocketHelper.is_socket_connected(sock):
            raise SdkException("Error occurred connecting to development socket")

        logging.info(f"Socket connection to {host}:{socket_port} established successfully")

        return sock

    @staticmethod
    def is_socket_connected(sock) -> bool:
        """Sends a simple message to the socket to see if it's connected

            Args:
                sock (socket): The socket object

            Returns:
                bool: True if the socket is connected, False otherwise
        """
        try:
            sock.send("test".encode("utf-8"))
            return True
        except socket.error as msg:
            logging.error(f"Socket not connected: {msg}")
            return False
