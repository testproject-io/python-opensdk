from src.testproject.enums.report_type import ReportType
from src.testproject.sdk.drivers import webdriver

DEV_TOKEN = "YOUR_DEV_TOKEN"


def test_local_report():
    driver = webdriver.Chrome(
        token=DEV_TOKEN,
        project_name="Report Decorator Project",
        job_name="Report Decorator Job",
        report_type=ReportType.LOCAL,
    )
    driver.report().disable_command_reports(True)
    driver.get(url="https://www.google.com")
    driver.report().step("Local Report - Navigating to URL", "Navigating to Google", True)
    driver.quit()


def test_cloud_report():
    driver = webdriver.Chrome(
        token=DEV_TOKEN,
        project_name="Report Decorator Project",
        job_name="Report Decorator Job",
        report_type=ReportType.CLOUD,
    )
    driver.report().disable_command_reports(True)
    driver.get(url="https://www.google.com")
    driver.report().step("Cloud Report - Navigating to URL", "Navigating to Google", True)
    driver.quit()


def test_cloud_and_local_report():
    driver = webdriver.Chrome(
        token=DEV_TOKEN,
        project_name="Report Decorator Project",
        job_name="Report Decorator Job",
        report_type=ReportType.CLOUD_AND_LOCAL,
    )
    driver.report().disable_command_reports(True)
    driver.get(url="https://www.google.com")
    driver.report().step("Local AND Cloud Report - Navigating to URL", "Navigating to Google", True)
    driver.quit()
