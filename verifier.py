"""This module provides the basic objects for the dataframe-validation"""

import logging
from dataclasses import dataclass
import pandas as pd


logging.basicConfig(level=logging.INFO)


@dataclass
class Verifier():
    """
    The DataVerifier class provides a way to verify constraints on a
    dataframe.
    """
    constraints: dict
    data: pd.DataFrame

    def __init__(self, data: pd.DataFrame, constraints: dict):
        """Init values"""
        self.constraints = constraints
        self.data = data

    def check_data_type(self, constraints: str, colname: str) -> bool:
        """Check data type against constraint"""
        return self.data[colname].dtype == constraints

    def check_nullable(self, constraints: str, colname: str) -> int:
        """Check null values against constraint"""
        if not constraints:
            nulls = self.data[colname].isna().sum()
        else:
            nulls = 0
        return nulls

    def check_unique(self, constraints: str, colname: str) -> int:
        """Check duplicate values against constraint"""
        return (~self.data[colname].duplicated().any() != constraints).sum()

    def check_max_length(self, constraints: str, colname: str) -> int:
        """Check max length against constraint"""
        return (self.data[colname].str.len() > constraints).sum()

    def check_min_length(self, constraints: str, colname: str) -> int:
        """Check min length against constraint"""
        return (self.data[colname].str.len() < constraints).sum()

    def check_value_range(self, constraints: str, colname: str) -> int:
        """Check range of values against constraint"""
        return (~self.data[colname].isin(constraints)).sum()

    def check_max_value(self, constraints: str, colname: str):
        """Check max value against constraint"""
        if self.data[colname].dtype.kind in "biufc":
            max_val = (self.data[colname] > constraints).sum()
        else:
            max_val = (
                    pd.to_datetime(self.data[colname],
                        infer_datetime_format=True) > constraints
                    ).sum()
        return max_val

    def check_min_value(self, constraints: str, colname: str):
        """Check min value against constraint"""
        if self.data[colname].dtype.kind in "biufc":
            min_val = (self.data[colname] < constraints).sum()
        else:
            min_val = (pd.to_datetime(self.data[colname],
                infer_datetime_format=True) < constraints).sum()
        return min_val

    def call_checks(self, check: str) -> dict:
        """
        Map constraint names with functions
        Params
        -----
        check: str

        Returns
        -----
        dict
            A dictionary of calculated constrainst.
        """
        checks_dict = {
                "nullable": self.check_nullable,
                "unique": self.check_unique,
                "max_length": self.check_max_length,
                "min_length": self.check_min_length,
                "value_range": self.check_value_range,
                "max_value": self.check_max_value,
                "min_value": self.check_min_value,
                "data_type": self.check_data_type
                }
        return checks_dict[check]

    def verify_data(self) -> pd.DataFrame:
        """
        Run all checks for the dataframe
        Params
        -----
        None: Uses object.data and object.constraints

        Returns
        -----
        pd.DataFrame
            A padas DataFrame with number of breaks per
            column.
        """
        verification = {}
        for col_index, value in self.constraints.items():
            logging.info("Validating %c.", col_index)
            verification[col_index] = {
                    check_key: self.call_checks(check_key)
                    (self.constraints[col_index][check_key], col_index)
                    for check_key, check_value in value.items()
                    }
        return pd.DataFrame(verification).T
