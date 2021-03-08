import pytest

from src.testproject.sdk.drivers import webdriver
from src.testproject.sdk.exceptions import InvalidTokenException, SdkException


def test_bad_token():
    with pytest.raises(expected_exception=InvalidTokenException):
        driver = webdriver.Chrome(token="bad_token")
        driver.quit()


def test_wrong_udid():
    with pytest.raises(expected_exception=SdkException, match="Requested device was not found"):
        desired_capabilities = {
            "appActivity": "host.exp.exponent.MainActivity",
            "appPackage": "com.example.tp",
            "udid": "11",
            "platformName": "Android",
            "unicodeKeyboard": "true",
            "resetKeyboard": "true",
        }

        driver = webdriver.Remote(desired_capabilities=desired_capabilities)
        driver.quit()


def test_wrong_browser_windows():
    with pytest.raises(expected_exception=SdkException, match="Could not discover browser Safari version."):
        driver = webdriver.Safari()
        driver.quit()
