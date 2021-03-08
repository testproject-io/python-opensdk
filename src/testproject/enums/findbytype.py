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

from enum import Enum, unique


@unique
class FindByType(Enum):
    """Enumeration of supported element locator strategies"""

    ID = "id"
    NAME = "name"
    CLASSNAME = "class name"
    CSSSELECTOR = "css selector"
    LINKTEXT = "link text"
    PARTIALLINKTEXT = "partial link text"
    TAG_NAME = "tag name"
    XPATH = "xpath"
    ACCESSIBILITYID = "accessibility id"
    IOSUIAUTOMATION = "-ios uiautomation"
    ANDROIDUIAUTOMATOR = "-android uiautomator"
    IOSPREDICATE = "-ios predicate string"
    IOSCLASSCHAIN = "-ios class chain"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
