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

from selenium.webdriver.common.by import By


class ProxyDescriptor:
    """Describes an Addon and an Action to be executed via the Agent

    Args:
        guid (str): a unique GUID used to identify the addon
        classname (str): the name of the action class that is contained in addon

    Attributes:
        _guid (str): a unique GUID used to identify the addon
        _classname (str): the name of the action class that is contained in the addon
        _by (By): Locator strategy for the element associated with this action
        _by_value (str): Corresponding locator strategy value
        _parameters (dict): parameters and their values associated with the action
    """

    def __init__(
        self,
        guid: str,
        classname: str,
    ):
        self._guid = guid
        self._classname = classname
        self._by = None
        self._by_value = None
        self._parameters: dict = {}

    @property
    def guid(self) -> str:
        """Getter for the action GUID"""
        return self._guid

    @guid.setter
    def guid(self, value: str):
        """Setter for the action GUID"""
        self._guid = value

    @property
    def classname(self) -> str:
        """Getter for the action class name"""
        return self._classname

    @classname.setter
    def classname(self, value: str):
        """Setter for the action class name"""
        self._classname = value

    @property
    def by(self) -> By:
        """Getter for the element locator strategy"""
        return self._by

    @by.setter
    def by(self, value: By):
        """Setter for the element locator strategy"""
        self._by = value

    @property
    def by_value(self) -> str:
        """Getter for the element locator value"""
        return self._by_value

    @by_value.setter
    def by_value(self, value: str):
        """Setter for the element locator value"""
        self._by_value = value

    @property
    def parameters(self) -> dict:
        """Getter for the action parameters"""
        return self._parameters

    @parameters.setter
    def parameters(self, value: dict):
        """Setter for the action parameters"""
        self._parameters = value
