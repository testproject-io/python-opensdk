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
import responses

from selenium.webdriver.common.by import By
from src.testproject.classes import ProxyDescriptor
from src.testproject.sdk.addons import ActionProxy
from src.testproject.rest.messages.agentstatusresponse import AgentStatusResponse
from src.testproject.sdk.exceptions import SdkException, AgentConnectException
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.helpers import ConfigHelper


@pytest.fixture()
def mocked_agent_address(mocker):
    # Mock the Agent address
    mocker.patch.object(ConfigHelper, "get_agent_service_address")
    ConfigHelper.get_agent_service_address.return_value = "http://localhost:9876"


@responses.activate
def test_get_agent_status_no_response_raises_sdkexception(mocked_agent_address):

    # Mock the response returned by the Agent when retrieving the address
    responses.add(responses.GET, "http://localhost:9876/api/status", status=200)

    with pytest.raises(SdkException) as sdke:
        AgentClient.get_agent_version(token="1234")
    assert (
        str(sdke.value)
        == "Could not parse Agent status response: no JSON response body present"
    )


@responses.activate
def test_get_agent_status_response_without_tag_element_raises_sdkexception(
    mocked_agent_address,
):

    # Mock the response returned by the Agent when retrieving the address
    responses.add(
        responses.GET,
        "http://localhost:9876/api/status",
        json={"key": "value"},
        status=200,
    )

    with pytest.raises(SdkException) as sdke:
        AgentClient.get_agent_version(token="1234")
    assert (
        str(sdke.value)
        == "Could not parse Agent status response: element 'tag' not found in JSON response body"
    )


@responses.activate
def test_get_agent_status_response_with_error_http_status_code_raises_agentconnectexception(
    mocked_agent_address,
):

    # Mock the response returned by the Agent when retrieving the address
    responses.add(responses.GET, "http://localhost:9876/api/status", status=500)

    with pytest.raises(AgentConnectException) as ace:
        AgentClient.get_agent_version(token="1234")
    assert (
        str(ace.value) == "Agent returned HTTP 500 when trying to retrieve Agent status"
    )


@responses.activate
def test_get_agent_status_response_with_tag_element_creates_agentstatusresponse(
    mocked_agent_address,
):

    # Mock the response returned by the Agent when retrieving the address
    responses.add(
        responses.GET,
        "http://localhost:9876/api/status",
        json={"tag": "1.2.3"},
        status=200,
    )

    agent_status_response: AgentStatusResponse = AgentClient.get_agent_version(
        token="1234"
    )
    assert agent_status_response.tag == "1.2.3"


def test_action_proxy_payload_is_correctly_formatted():
    # Arrange - Create a custom proxy descriptor
    proxy_descriptor = ProxyDescriptor("my_guid", "my_classname")
    proxy_descriptor.by = By.CSS_SELECTOR
    proxy_descriptor.by_value = "my_css_selector"
    proxy_descriptor.parameters = {"key": "value"}

    # Arrange - Create an action proxy object
    action_proxy = ActionProxy()
    action_proxy.proxydescriptor = proxy_descriptor

    # Act - Create the payload that will be sent to the Agent to execute this action
    payload = AgentClient._create_action_proxy_payload(action_proxy)

    # Assert - Check that the payload contains the expected keys and associated values
    assert payload["by"] == {"cssSelector": "my_css_selector"}
    assert payload["className"] == "my_classname"
    assert payload["guid"] == "my_guid"
    assert payload["parameters"] == {"key": "value"}
