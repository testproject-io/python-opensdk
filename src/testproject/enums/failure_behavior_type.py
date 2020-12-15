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

from enum import Enum


class FailureBehaviorType(Enum):
    """Enum that represents step's failure behavior timing type."""
    Abort = 1
    Continue = 2
    RecoveryAbort = 3
    RecoveryContinue = 4
    RecoveryRepeatStep = 5
    RecoveryRepeatTest = 6
    Inherit = 7
    AlwaysPass = 8
