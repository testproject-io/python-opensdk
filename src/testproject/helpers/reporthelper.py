# Copyright 2020 TestProject (https://testproject.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import ntpath
import os
import inspect

from src.testproject.enums import EnvironmentVariable, ReportNamingElement


class ReportHelper:
    """Provides helper functions used in reporting command, tests and steps"""

    @classmethod
    def infer_test_name(cls) -> str:
        """Tries to infer the test name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred test name (typically the test method name)
        """
        # Did we set the test name using our decorator?
        test_name_in_decorator = os.environ.get(EnvironmentVariable.TP_TEST_NAME.value)
        if test_name_in_decorator is not None:
            return test_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            result = cls.infer_name_from_pytest_info_for(
                current_test_info, ReportNamingElement.Test
            )
        else:
            # Try finding the right entry in the call stack (for unittest or when no testing framework is used)
            logging.debug("Attempting to infer test name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Test)
            logging.debug(f"Inferred test name '{result}' from inspect.stack()")

        return result if result is not None else "Unnamed Test"

    @classmethod
    def infer_project_name(cls) -> str:
        """Tries to infer the project name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred project name (typically the folder containing the test file)
        """
        # Did we set the project name using our decorator?
        project_name_in_decorator = os.environ.get(
            EnvironmentVariable.TP_PROJECT_NAME.value
        )
        if project_name_in_decorator is not None:
            return project_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            result = cls.infer_name_from_pytest_info_for(
                current_test_info, ReportNamingElement.Project
            )
        else:
            # Try finding the right entry in the call stack (for unittest or when no testing framework is used)
            logging.debug("Attempting to infer project name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Project)
            logging.debug(f"Inferred project name '{result}' from inspect.stack()")

        return result if result is not None else "Unnamed Project"

    @classmethod
    def infer_job_name(cls) -> str:
        """Tries to infer the job name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred job name (typically the test file name (without the .py extension)
        """
        # Did we set the job name using our decorator?
        job_name_in_decorator = os.environ.get(EnvironmentVariable.TP_JOB_NAME.value)
        if job_name_in_decorator is not None:
            return job_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            result = cls.infer_name_from_pytest_info_for(
                current_test_info, ReportNamingElement.Job
            )
        else:
            # Try finding the right entry in the call stack (for unittest or when no testing framework is used)
            logging.debug("Attempting to infer job name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Job)
            logging.debug(f"Inferred job name '{result}' from inspect.stack()")

        return result if result is not None else "Unnamed Job"

    @classmethod
    def infer_name_from_pytest_info_for(
        cls, pytest_info: str, element_to_find: ReportNamingElement
    ):
        """Uses the test info stored by pytest to infer a project, job or test name

        Args:
            pytest_info (str): the test info as stored by pytest
            element_to_find (ReportNamingElement): the report naming element that we're looking for

        Returns:
            str: the inferred report naming element value
        """
        path_to_test_file = pytest_info.split(" ")[0].split("::")[0]
        if element_to_find == ReportNamingElement.Project:
            # Return the path without base file name parsed as "package".s
            return path_to_test_file[0: path_to_test_file.rfind("/")].replace("/", ".")
        elif element_to_find == ReportNamingElement.Job:
            # Return the base file name without '.py' extension.
            head, tail = ntpath.split(path_to_test_file)
            return (tail or ntpath.basename(head)).split(".py")[0]
        elif element_to_find == ReportNamingElement.Test:
            return pytest_info.rsplit(" ", maxsplit=1)[0].split("::")[1]
        return None

    @classmethod
    def __find_name_in_call_stack_for(cls, element_to_find: ReportNamingElement) -> str:
        """Uses the current call stack to try and infer a project, job or test name

        Args:
            element_to_find (ReportNamingElement): the report naming element that we're looking for

        Returns:
            str: the inferred report naming element value
        """
        is_unittest = cls.__detect_unittest()

        if is_unittest:
            if element_to_find in [
                ReportNamingElement.Project,
                ReportNamingElement.Job,
            ]:
                # A driver can be initialized inside a test method, but also in a fixture method
                # Therefore we want to look for all these methods when we try to infer project and job names
                # (since project and job names are sent to the Agent upon driver creation)
                for frame in inspect.stack().__reversed__():
                    if frame.function.startswith("test") or frame.function in [
                        "setUp",
                        "tearDown",
                        "setUpClass",
                        "tearDownClass",
                    ]:
                        if element_to_find == ReportNamingElement.Project:
                            path_elements = os.path.normpath(frame.filename).split(
                                os.sep
                            )
                            # return the folder name containing the current test file as the project name
                            return str(path_elements[-2])
                        elif element_to_find == ReportNamingElement.Job:
                            path_elements = os.path.normpath(frame.filename).split(
                                os.sep
                            )
                            # return the current test file name minus the .py extension as the job name
                            return str(path_elements[-1]).split(".py")[0]
                        else:
                            return None
            else:
                # When inferring test names, we are only interested in those methods whose name
                # actually starts with 'test', not in fixture methods
                for frame in inspect.stack().__reversed__():
                    if frame.function.startswith("test"):
                        if element_to_find == ReportNamingElement.Test:
                            # return the current method name as the test name
                            return frame.function
                return None

        else:
            # we're using neither pytest nor unittest, so return sensible values
            inside_module = False

            for frame in inspect.stack().__reversed__():
                if inside_module:
                    if element_to_find == ReportNamingElement.Test:
                        return frame.function
                    elif element_to_find == ReportNamingElement.Project:
                        # in this case we can't infer a project name because there's no data
                        return None
                    elif element_to_find == ReportNamingElement.Job:
                        path_elements = os.path.normpath(frame.filename).split(os.sep)
                        # return the current test file name minus the .py extension as the job name
                        return str(path_elements[-1]).split(".py")[0]
                if str(frame.function) == "<module>":
                    # we're entering the module, the next frame contains the info we're looking for
                    inside_module = True

    @classmethod
    def __detect_unittest(cls) -> bool:
        """Utility method that traverses the call stack and checks if unittest was invoked

        Returns:
            bool: True if unittest was found in the call stack, False otherwise
        """
        for frame in inspect.stack().__reversed__():
            if (
                frame.function == "__init__"
                and str(frame.filename).find("unittest") > 0
                and str(frame.filename).find("main.py") > 0
            ):
                return True
        return False

    @classmethod
    def find_unittest_teardown(cls) -> bool:
        """Utility method that traverses the call stack and checks if unittest was invoked

        Returns:
            bool: True if unittest was found in the call stack, False otherwise
        """
        if not cls.__detect_unittest():
            return False
        else:
            for frame in inspect.stack().__reversed__():
                if frame.function in ["tearDown", "tearDownClass"]:
                    return True
        return False
