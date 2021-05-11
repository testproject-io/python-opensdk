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

from importlib_metadata import metadata, PackageNotFoundError
from src.testproject.sdk.exceptions import SdkException


def get_sdk_version() -> str:
    """Returns the current SDK version

    Returns:
        str: The current SDK version read from package metadata or an environment variable
    """

    version = None

    try:
        sdk_metadata = metadata("testproject-python-sdk")
        version = sdk_metadata["Version"]
    except PackageNotFoundError:
        # This is OK, it just means that there's no previously installed version available
        pass

    logging.debug(f"Version read from package metadata: {version}")

    if version is None:
        # we're not dealing with an installed package, build uses an environment variable
        version = os.environ.get("TP_SDK_VERSION")
        if version is None:
            raise SdkException("No SDK version definition found in metadata or environment variable")

        logging.debug(f"Version read from environment variable: {version}")

    # Sanitize the agent version to return only x.x.x
    if "-" in version:
        version = version.split("-")[0]

    return version
