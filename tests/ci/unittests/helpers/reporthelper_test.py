from src.testproject.helpers import ReportHelper


def test_test_name_is_inferred_correctly():
    assert ReportHelper.infer_test_name() == "test_test_name_is_inferred_correctly"


def test_project_name_is_inferred_correctly():
    assert ReportHelper.infer_project_name() == "tests.ci.unittests.helpers"


def test_job_name_is_inferred_correctly():
    assert ReportHelper.infer_job_name() == "reporthelper_test"
