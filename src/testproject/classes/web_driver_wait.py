import os
import json
from typing import Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from src.testproject.classes import DriverStepSettings, StepSettings
from src.testproject.sdk.drivers.webdriver import Remote
from src.testproject.sdk.drivers.webdriver.base import BaseDriver


class TestProjectWebDriverWait(WebDriverWait):
    """Wrapper class for the WebDriverWait.

    WebDriverWait uses until/until_not functions, these functions can call a certain driver command more than once.
    Moreover, the evaluated step result doesn't have to match the result of the driver command.
    For Example:
        until(title_is(title)) will execute driver.title which in itself will work (as a driver command)
        but that doesnt guarantee that the title is the expected title.
    Due to the above, this wrapper class handles the step reporting and user defined step settings.
    """
    def __init__(self, driver: Union[BaseDriver, Remote], timeout):
        super().__init__(driver, timeout)
        self._driver = driver

    def until(self, method, message=''):
        """Executes the wrapping function for until."""
        return self.execute("until", method, message)

    def until_not(self, method, message=''):
        """Executes the wrapping function for until_not."""
        return self.execute("until_not", method, message)

    def execute(self, function_name, method, message):
        """Executes the function (until/until_not) silently (without reports/settings).

        This execution will take into account the defined step settings and will handle them only once before silently
        executing the function.
        Based on the function's result and given method, it will report this Step with all the needed information.
        Returns the result of the executed function.
        """
        timeout_exception = None
        step_helper = self.driver.command_executor.step_helper
        step_settings = self.driver.command_executor.settings
        # Disable reports
        self._driver.report().disable_reports(True)
        # Handle driver timeout
        step_helper.handle_timeout(timeout=step_settings.timeout)
        # Handle sleep before
        step_helper.handle_sleep(sleep_timing_type=step_settings.sleep_timing_type,
                                 sleep_time=step_settings.sleep_time)
        # Execute the function with default StepSettings.
        with DriverStepSettings(self._driver, StepSettings()):
            try:
                result = getattr(super(), function_name)(method, message)
            except TimeoutException as e:
                result = False
                timeout_exception = e
        # Handle sleep after
        step_helper.handle_sleep(sleep_timing_type=step_settings.sleep_timing_type,
                                 sleep_time=step_settings.sleep_time, step_executed=True)
        # Handle result
        result, step_message = step_helper.handle_step_result(step_result=result,
                                                              invert_result=step_settings.invert_result,
                                                              always_pass=step_settings.always_pass)
        # Handle screenshot condition
        screenshot = step_helper.take_screenshot(step_settings.screenshot_condition, result)

        # Enable reports and report the step result with all execution details.
        self._driver.report().disable_reports(False)

        # Inferring function name - until / until not
        function_name = ' '.join(function_name.split('_'))
        # Getting all additional step information.
        step_name, step_attributes = self.get_report_details(method)
        self._driver.report().step(description=f'Wait {function_name} {step_name}',
                                   message=f'{step_message}{os.linesep}',
                                   passed=result,
                                   inputs=step_attributes,
                                   screenshot=screenshot)
        # Always pass ignore result and thrown exception.
        if step_settings.always_pass:
            return True
        # Raise exception if there was one.
        if timeout_exception:
            raise timeout_exception
        return result

    def get_report_details(self, method):
        """Returns the inferred report details.

        Step name is the method class's name, underscores are replaces with spaces.
        Attributes dict is all the method's attributes and their values.
        """
        step_name = ' '.join(method.__class__.__name__.split('_'))
        attributes_dict = {attribute: json.dumps(getattr(method, attribute))
                           for attribute in self.get_user_attributes(method)}
        return step_name, attributes_dict

    @staticmethod
    def get_user_attributes(cls, exclude_methods=True):
        """Gets a class's user defined attributes, ignores methods by default."""
        base_attrs = dir(type('dummy', (object,), {}))
        this_cls_attrs = dir(cls)
        res = []
        for attr in this_cls_attrs:
            if base_attrs.count(attr) or (callable(getattr(cls, attr)) and exclude_methods):
                continue
            res += [attr]
        return res

    @property
    def driver(self):
        """Getter for the driver."""
        return self._driver
