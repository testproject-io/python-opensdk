from enum import Enum, unique


@unique
class ReportNamingElement(Enum):
    """Enum containing types of report elements that can be inferred"""

    Project = 1
    Job = 2
    Test = 3
