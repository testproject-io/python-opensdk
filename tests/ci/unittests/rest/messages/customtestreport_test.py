from src.testproject.rest.messages import CustomTestReport


def test_to_json():
    test_result_report = CustomTestReport(name="my_name", passed=True, message="my_message")
    assert test_result_report.to_json() == {
        "name": "my_name",
        "passed": True,
        "message": "my_message",
    }
