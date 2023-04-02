"""This module provides the basic objects for the dataframe_validation"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class StandardVerifier:
    """
    The DataVerifier class provides a way to verify constraints on a
    dataframe.
    """

    data: pd.DataFrame
    constraints: dict
    enforce_dtypes: bool = False

    def __post_init__(self):
        "Post init calculations."
        self.failed_rows = []
        self.validation_summary = self.__validate_data()
        self.validation_data: pd.DataFrame = self.__get_validation_data()

    def check_data_type(self, constraint: str, col: str) -> bool:
        """Check data type against constraint"""
        return self.data[col].dtype.name != constraint

    def check_nullable(self, constraint: bool, col: str) -> int:
        """Check null values against constraint"""
        if not constraint:
            breaks = self.data[col].isna()
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"nullable: {col}"
            self.failed_rows.append(rows)
        else:
            breaks = pd.Series(False)
        return breaks.sum()

    def check_unique(self, constraint: bool, col: str) -> int:
        """Check duplicate values against constraint"""
        if constraint:
            breaks = (self.data[col].notna()) & (self.data[col].duplicated())
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"unique: {col}"
            self.failed_rows.append(rows)
        else:
            breaks = pd.Series(False)
        return breaks.sum()

    def check_max_length(self, constraint: int, col: str) -> int:
        """Check max length against constraint"""
        if not pd.api.types.is_numeric_dtype(self.data[col]):
            breaks = (self.data[col].notna()) & (
                self.data[col].astype(str).str.len() > constraint
            )
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"max_length: {col}"
            self.failed_rows.append(rows)
            return breaks.sum()
        return None

    def check_min_length(self, constraint: int, col: str) -> int:
        """Check min length against constraint"""
        if not pd.api.types.is_numeric_dtype(self.data[col]):
            breaks = (self.data[col].notna()) & (
                self.data[col].astype(str).str.len() < constraint
            )
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"min_legth:{col}"
            self.failed_rows.append(rows)
            return breaks.sum()
        return None

    def check_value_range(self, constraint: list, col: str) -> int:
        """Check range of values against constraint"""
        breaks = (self.data[col].notnull()) & (
            ~self.data[col].isin(constraint)
        )
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"value_range: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_max_value(self, constraint: str, col: str):
        """Check max value against constraint"""
        breaks = self.data[col] > constraint
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_value: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_min_value(self, constraint: str, col: str):
        """Check min value against constraint"""
        breaks = self.data[col] < constraint
        rows = self.data.loc[breaks].copy()
        rows["Validation"] = f"max_value: {col}"
        self.failed_rows.append(rows)
        return breaks.sum()

    def check_min_date(self, constraint: str, col: str) -> int:
        """Check min date against constraint"""
        if pd.api.types.is_datetime64_dtype(self.data[col]):
            breaks = pd.to_datetime(
                pd.Series(self.data[col], dtype="datetime64[ns]")
            ) < pd.to_datetime(constraint)
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"min_date: {col}"
            self.failed_rows.append(rows)
            return breaks.sum()
        return None

    def check_max_date(self, constraint: str, col: str) -> int:
        """Check max date against constraint"""
        if pd.api.types.is_datetime64_dtype(self.data[col]):
            breaks = pd.to_datetime(
                pd.Series(self.data[col], dtype="datetime64[ns]")
            ) > pd.to_datetime(constraint)
            rows = self.data.loc[breaks].copy()
            rows["Validation"] = f"max_date: {col}"
            self.failed_rows.append(rows)
            return breaks.sum()
        return None

    def _call_checks(self, check: str) -> dict:
        """
        Map constraint names with functions.
        :param check: a str of check type
        :return: a dict of calculated constraints
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
            "min_date": self.check_min_date,
        }
        return checks_dict[check]

    def __validate_data(self) -> pd.DataFrame:
        """
        Run all checks for the DataFrame
        :param enforce_dtypes: a bool to enforce constraint dtype on validation
        :return: a DataFrame with number of breaks per column
        """
        if self.enforce_dtypes:
            dtypes = {
                out_key: in_val
                for out_key, out_val in self.constraints.items()
                for in_key, in_val in out_val.items()
                if in_key == "data_type"
            }
            self.data = self.data.astype(dtypes)

        verification = {}
        for col_index, value in self.constraints.items():
            verification[col_index] = {
                check_key: self._call_checks(check_key)(
                    self.constraints[col_index][check_key], col_index
                )
                for check_key, check_value in value.items()
            }
        return pd.DataFrame(verification)

    def __get_validation_data(self) -> pd.DataFrame:
        """
        Gets all DataFrame rows with validation breaks.
        :param: None
        :returns: a DataFrame with rows of validation breaks
        """
        failed_data = pd.concat(self.failed_rows)
        return failed_data


@dataclass
class CustomVerifier:
    """
    The DataVerifier class provides a way to verify constraints on a
    dataframe.
    """

    data: pd.DataFrame
    constraints: list

    def __post_init__(self):
        "Post init calculations."
        self.failed_rows = []
        self.validation_summary = self.__validate_data()
        self.validation_data: pd.DataFrame = self.__get_validation_data()

    def check_custom_constraints(self, constraint: dict) -> dict:
        """
        Check custom constraints
        :param constraint: a custom constraint dict with name and query keys
        :return: an int with count of breaks
        """

        rows = self.data.query(constraint["query"], engine="python").copy()
        rows["Validation"] = f"{constraint['name']}: {constraint['query']}"
        self.failed_rows.append(rows)
        return rows.shape[0]

    def __validate_data(self) -> pd.DataFrame:
        """
        Run all checks for the dataframe
        :param: None
        :returns: a DataFrame with number of breaks per column
        """
        verification = {}
        for constraint in self.constraints:
            verification[constraint["name"]] = {
                    "name": constraint["name"],
                    "rule": constraint["query"],
                    "count": self.check_custom_constraints(constraint)
                    }
        summary = pd.DataFrame(verification).T.reset_index()
        return summary[["name", "rule", "count"]]

    def __get_validation_data(self) -> pd.DataFrame:
        """
        Gets all dataframe rows with validation breaks.
        :param None:
        :returns: a DataFrame with rows of validation breaks
        """
        failed_data = pd.concat(self.failed_rows)
        return failed_data
