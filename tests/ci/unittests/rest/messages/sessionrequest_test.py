from src.testproject.helpers import ConfigHelper
from src.testproject.rest import ReportSettings
from src.testproject.rest.messages import SessionRequest


def test_sessionrequest_to_json(mocker):
    # mock the response to get_sdk_version() as this will change over time
    mocker.patch.object(ConfigHelper, "get_sdk_version")
    ConfigHelper.get_sdk_version.return_value = "1.2.3.4"

    capabilities = {"key": "value"}
    reportsettings = ReportSettings("my_project", "my_job")
    session_request = SessionRequest(capabilities, reportsettings)
    assert session_request.to_json() == {
        "projectName": "my_project",
        "jobName": "my_job",
        "capabilities": {"key": "value"},
        "sdkVersion": "1.2.3.4",
        "language": "Python",
    }
