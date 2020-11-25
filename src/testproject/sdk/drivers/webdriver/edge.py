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

from selenium.webdriver.edge.options import Options
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


class Edge(BaseDriver):
    """Used to create a new Edge browser instance

    Args:
        edge_options (Options): Edge automation session desired capabilities and options
        desired_capabilities (dict): Dictionary object containing desired capabilities for Chrome automation session
        token (str): The developer token used to communicate with the agent
        projectname (str): Project name to report
        jobname (str): Job name to report
        disable_reports (bool): set to True to disable all reporting (no report will be created on TestProject)
    """

    def __init__(
        self,
        edge_options: Options = None,
        desired_capabilities: dict = None,
        token: str = None,
        projectname: str = None,
        jobname: str = None,
        disable_reports: bool = False,
    ):
        # If no options or capabilities are specified at all, use default Options
        if edge_options is None and desired_capabilities is None:
            caps = Options().to_capabilities()
        else:
            # Specified EdgeOptions take precedence over desired capabilities but either can be used
            caps = (
                edge_options.to_capabilities()
                if edge_options is not None
                else desired_capabilities
            )

        super().__init__(
            capabilities=caps,
            token=token,
            projectname=projectname,
            jobname=jobname,
            disable_reports=disable_reports,
        )
