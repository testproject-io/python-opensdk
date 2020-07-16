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

from src.testproject.classes import ElementSearchCriteria
from src.testproject.enums import FindByType


def test_to_json_with_default_arguments():
    esc_json = ElementSearchCriteria(FindByType.XPATH, "//xpath").to_json()
    assert esc_json == {"byType": "XPATH", "byValue": "//xpath", "index": -1}


def test_to_json_with_custom_arguments():
    esc_json = ElementSearchCriteria(FindByType.CSSSELECTOR, "#cssselector", 5).to_json()
    assert esc_json == {"byType": "CSSSELECTOR", "byValue": "#cssselector", "index": 5}
