"""This module provides the basic objects for the dataframe_validation"""

from dataclasses import dataclass


@dataclass
class CustomConstraint:
    """
    The Constraints class provides a data constraints discovery.
    """

    name: str
    query: str
