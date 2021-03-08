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


class ResultField:
    """Object representing a field associated with an action

    Attributes:
        _name (str): The field name
        _value: the field value
        _is_output (bool): True if the field is an output field, False otherwise
    """

    def __init__(self, name: str = None, value=None, output: bool = None):
        self._name = name
        self._value = value
        self._is_output = output

    @property
    def name(self) -> str:
        """Getter for the field name"""
        return self._name

    @name.setter
    def name(self, value: str):
        """Setter for the field name"""
        self._name = value

    @property
    def value(self):
        """Getter for the field value"""
        return self._value

    @value.setter
    def value(self, val):
        """Setter for the field value"""
        self._value = val

    @property
    def is_output(self) -> bool:
        """Getter for the field is_output indication"""
        return self._is_output

    @is_output.setter
    def is_output(self, value: bool):
        """Setter for the field is_output indication"""
        self._is_output = value
