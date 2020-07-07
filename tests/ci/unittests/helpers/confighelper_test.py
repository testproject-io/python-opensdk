import pytest

from src.testproject.helpers import ConfigHelper
from src.testproject.sdk.exceptions import SdkException


def test_undefined_agent_env_variable_resolves_to_default_agent_service_address(monkeypatch,):
    monkeypatch.delenv("TP_AGENT_URL", raising=False)
    assert ConfigHelper.get_agent_service_address() == "http://127.0.0.1:8585"


def test_predefined_agent_env_variable_resolves_to_specified_value(monkeypatch):
    monkeypatch.setenv("TP_AGENT_URL", "some_address")
    assert ConfigHelper.get_agent_service_address() == "some_address"


def test_undefined_token_env_variable_leads_to_exception_raised(monkeypatch):
    monkeypatch.delenv("TP_DEV_TOKEN", raising=False)
    with pytest.raises(SdkException) as sdke:
        ConfigHelper.get_developer_token()
    assert str(sdke.value) == "No development token defined in TP_DEV_TOKEN environment variable"


def test_predefined_token_env_variable_resolves_to_specified_value(monkeypatch):
    monkeypatch.setenv("TP_DEV_TOKEN", "some_token")
    assert ConfigHelper.get_developer_token() == "some_token"
