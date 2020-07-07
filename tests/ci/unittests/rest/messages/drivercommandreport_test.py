import pytest

from src.testproject.rest.messages import DriverCommandReport


@pytest.fixture
def dcr():
    return DriverCommandReport("command", {"param": "value"}, {"result": "value"}, True)


def test_instances_with_same_arguments_are_considered_equal(dcr):

    another_dcr = DriverCommandReport("command", {"param": "value"}, {"result": "value"}, True)

    assert another_dcr is not dcr
    assert another_dcr == dcr


def test_instances_with_different_arguments_are_considered_not_equal(dcr):

    another_dcr = DriverCommandReport("command", {"param": "value"}, {"result": "another_value"}, True)

    assert another_dcr is not dcr
    assert another_dcr != dcr


def test_to_json(dcr):
    assert dcr.to_json() == {
        "commandName": "command",
        "commandParameters": {"param": "value"},
        "result": {"result": "value"},
        "passed": True,
    }
