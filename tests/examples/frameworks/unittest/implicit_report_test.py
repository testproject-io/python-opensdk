import unittest

from src.testproject.sdk.drivers import webdriver
from tests.pageobjects.web import LoginPage, ProfilePage


class TestBasic(unittest.TestCase):
    def test_login_to_testproject_demo_app(self):
        driver = webdriver.Chrome()
        LoginPage(driver).open().login_as("John Smith", "12345")
        assert ProfilePage(driver).greetings_are_displayed() is True
        driver.quit()


if __name__ == "__main__":
    unittest.main()
