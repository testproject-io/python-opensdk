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

from src.testproject.tcp import SocketManager


class AgentClientSingleton(type):
    """
    Singleton class which defines the behaviour of getting and setting an AgentClient instance.
    This class returns the instance of the AgentClient if it exists, as well as creates it if it does not,
    it also checks if the agent dev session should be reused before returning the instance, for aggregating
    test reports which use the same ReportSettings (Job and Project name).
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Create an instance of it does not exist
            cls._instances[cls] = super(AgentClientSingleton, cls).__call__(*args, **kwargs)
        else:
            # An instance already exists, check if it has the same designated Job and Project name
            input_settings = kwargs["report_settings"]
            instance = cls._instances[cls]
            report_settings = instance.report_settings

            same_settings = True if input_settings is not None and input_settings == report_settings else False

            # Stop the current instance, and submit the reports to the reports Queue
            instance.stop()

            if not same_settings or not instance.can_reuse_session():
                # Close the socket, as the settings are not the same hence different reports need to be generated
                SocketManager.instance().close_socket()

            # Init the instance to start the new Test
            instance.__init__(*args, **kwargs)

        return cls._instances[cls]
