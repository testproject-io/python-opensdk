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

import pytest

from urllib.parse import urljoin
from src.testproject.helpers import ConfigHelper
from src.testproject.sdk.exceptions import SdkException
from src.testproject.sdk.internal.agent.agent_client import Endpoint


def test_undefined_agent_env_variable_resolves_to_default_agent_service_address(
    monkeypatch,
):
    monkeypatch.delenv("TP_AGENT_URL", raising=False)
    assert ConfigHelper.get_agent_service_address() == "http://127.0.0.1:8585"


def test_predefined_agent_env_variable_resolves_to_specified_value(monkeypatch):
    monkeypatch.setenv("TP_AGENT_URL", "some_address")
    assert ConfigHelper.get_agent_service_address() == "some_address"


def test_agent_env_with_trailing_slash_is_handled_correctly(monkeypatch):
    monkeypatch.setenv("TP_AGENT_URL", "http://localhost:8585/")
    agent_address = ConfigHelper.get_agent_service_address()
    assert (
        urljoin(agent_address, Endpoint.DevelopmentSession.value)
        == "http://127.0.0.1:8585/api/development/session"
    )


def test_undefined_token_env_variable_leads_to_exception_raised(monkeypatch):
    monkeypatch.delenv("TP_DEV_TOKEN", raising=False)
    with pytest.raises(SdkException) as sdke:
        ConfigHelper.get_developer_token()
    assert (
        str(sdke.value)
        == "No development token defined in TP_DEV_TOKEN environment variable"
    )


def test_predefined_token_env_variable_resolves_to_specified_value(monkeypatch):
    monkeypatch.setenv("TP_DEV_TOKEN", "some_token")
    assert ConfigHelper.get_developer_token() == "some_token"
