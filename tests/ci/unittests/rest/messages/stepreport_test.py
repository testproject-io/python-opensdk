import uuid

from src.testproject.rest.messages import StepReport


def test_to_json_without_screenshot(mocker):
    # mock the response to uuid4() as this will change each time
    mocker.patch.object(uuid, "uuid4")
    uuid.uuid4.return_value = "12-ab-34-cd"

    step_report = StepReport(description="my_description", message="my_message", passed=True)
    assert step_report.to_json() == {
        "guid": "12-ab-34-cd",
        "description": "my_description",
        "message": "my_message",
        "passed": True,
    }


def test_to_json_with_screenshot(mocker):
    # mock the response to uuid4() as this will change each time
    mocker.patch.object(uuid, "uuid4")
    uuid.uuid4.return_value = "56-ef-78-gh"

    step_report = StepReport(
        description="another_description", message="another_message", passed=False, screenshot="base64_screenshot_here",
    )
    assert step_report.to_json() == {
        "guid": "56-ef-78-gh",
        "description": "another_description",
        "message": "another_message",
        "passed": False,
        "screenshot": "base64_screenshot_here",
    }
