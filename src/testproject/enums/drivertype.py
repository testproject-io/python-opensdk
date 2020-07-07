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
class DriverType(Enum):
    NoDriver = 1
    Safari = 2
    Chrome = 3
    Firefox = 4
    Marionette = 5
    InternetExplorer = 6
    Edge = 7
    Opera = 8
    Appium_Android = 9
    Appium_Android_Chrome = 10
    Appium_Android_Chromium = 11
    Appium_Android_Browser = 12
    Appium_iOS = 13
    Appium_iOS_Safari = 14
    Selendroid = 15
    iOSDriver = 16
    SauceLabs = 17
    BrowserStack = 18
