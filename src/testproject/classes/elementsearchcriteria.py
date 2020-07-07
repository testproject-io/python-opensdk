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
from src.testproject.enums import FindByType


class ElementSearchCriteria:
    def __init__(self, find_by_type: FindByType, by_value: str, index: int = -1):
        self._find_by_type = find_by_type
        self._by_value = by_value
        self._index = index

    @property
    def find_by_type(self) -> FindByType:
        return self._find_by_type

    @find_by_type.setter
    def find_by_type(self, value: FindByType):
        self._find_by_type = value

    @property
    def by_value(self) -> str:
        return self._by_value

    @by_value.setter
    def by_value(self, value: str):
        self._by_value = value

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    def to_json(self):
        return {
            "byType": self._find_by_type.name,
            "byValue": self._by_value,
            "index": self._index,
        }
