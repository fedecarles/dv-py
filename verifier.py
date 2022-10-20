"""This module provides the basic objects for the dataframe_validation"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class Verifier():
    """
    The DataVerifier class provides a way to verify constraints on a
    dataframe.
    """
    data: pd.DataFrame()
    constraints: dict

    def __post_init__(self):
        "Post init calculations."
        self.failed_rows = []
        self.validation_summary: pd.DataFrame = self.__validate_data()
        self.validation_data: pd.DataFrame = self.__get_validation_data()

    def check_data_type(self, constraint: str, col: str) -> bool:
        """Check data type against constraint"""
        return self.data[col].dtype.name != constraint

    def check_nullable(self, constraint: str, col: str) -> int:
        """Check null values against constraint"""
        if not constraint:
            breaks = self.data[col].isna()
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"nullable: {col}"
            self.failed_rows.append(rows)
        else:
            breaks = pd.Series(False)
        return breaks.sum()

    def check_unique(self, constraint: str, col: str) -> int:
        """Check duplicate values against constraint"""
        if constraint:
            breaks = self.data[col].duplicated()
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"unique: {col}"
            self.failed_rows.append(rows)
        else:
            breaks = pd.Series(False)
        return breaks.sum()

    def check_max_length(self, constraint: str, col: str) -> int:
        """Check max length against constraint"""
        breaks = (self.data[col].str.len() > constraint)
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_length: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_min_length(self, constraint: str, col: str) -> int:
        """Check min length against constraint"""
        breaks = (self.data[col].str.len() < constraint)
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"min_legth:{col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_value_range(self, constraint: list, col: str) -> int:
        """Check range of values against constraint"""
        breaks = (self.data[col].notnull()) &\
                 (~self.data[col].isin("constraint"))
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"value_range: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_max_value(self, constraint: str, col: str):
        """Check max value against constraint"""
        breaks = (self.data[col] > constraint)
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_value: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_min_value(self, constraint: str, col: str):
        """Check min value against constraint"""
        breaks = (self.data[col] < constraint)
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_value: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_min_date(self, constraint: str, col: str) -> int:
        """Check min date against constraint"""
        breaks = (
                pd.to_datetime(
                    self.data[col],
                    infer_datetime_format=True) < pd.to_datetime(constraint)
                )
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"min_date: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_max_date(self, constraint: str, col: str) -> int:
        """Check max date against constraint"""
        breaks = (
                pd.to_datetime(self.data[col],
                    infer_datetime_format=True) > pd.to_datetime(constraint)
                )
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_date: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def _call_checks(self, check: str) -> dict:
        """
        Map constraint names with functions.
        Parameters:
            check: a str of check type
        Returns:
            A dict of calculated constraints
        """
        checks_dict = {
                "data_type": self.check_data_type,
                "nullable": self.check_nullable,
                "unique": self.check_unique,
                "max_length": self.check_max_length,
                "min_length": self.check_min_length,
                "value_range": self.check_value_range,
                "max_value": self.check_max_value,
                "min_value": self.check_min_value,
                "max_date": self.check_max_date,
                "min_date": self.check_min_date
                }
        return checks_dict[check]

    def __validate_data(self) -> pd.DataFrame:
        """
        Run all checks for the dataframe
        Parameters:
            None: Uses object.data and object.constraints
        Returns:
            A pandas DataFrame with number of breaks per column
        """
        verification = {}
        for col_index, value in self.constraints.items():
            verification[col_index] = {
                    check_key: self._call_checks(check_key)
                    (self.constraints[col_index][check_key], col_index)
                    for check_key, check_value in value.items()
                    }
        return pd.DataFrame(verification)

    def __get_validation_data(self) -> pd.DataFrame:
        """
        Gets all dataframe rows with validation breaks.
        Parameters:
            None: Uses object.data and object.constraints
        Returns:
            A pandas DataFrame with rows of validation breaks
        """
        failed_data = pd.concat(self.failed_rows)
        return failed_data
