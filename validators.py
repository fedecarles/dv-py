"""This module provides the basic objects for the dataframe-validation"""

import numbers
import logging
import pandas as pd
from dataclasses import dataclass


@dataclass
class DataParser():
    """
    The DataParser class contains functions to optimize and
    prepare a pandas DataFrame
    """
    df: pd.DataFrame()

    def __init__(self, df):
        self.df = df
        self._optimize_dtypes()
        self._guess_date_types()

    def _guess_date_types(self) -> pd.DataFrame:
        """Convert date columns to datetime"""
        date_cols = self.df.filter(
                regex='Fecha|date|dt|DT|Date|maturity|EROD'
                ).columns
        for date in date_cols:
            self.df[date] = pd.to_datetime(
                    self.df[date],
                    errors='ignore',
                    infer_datetime_format=True).astype('datetime64[ns]')
        return self.df

    def _optimize_dtypes(self) -> pd.DataFrame:
        """Optimize data types"""
        for col in self.df.columns:
            if issubclass(self.df[col].dtypes.type, numbers.Integral):
                self.df[col] = pd.to_numeric(self.df[col], downcast='integer')
            elif issubclass(self.df[col].dtypes.type, numbers.Real):
                self.df[col] = pd.to_numeric(self.df[col], downcast='float')
            elif issubclass(self.df[col].dtypes.type, object) \
                    and (self.df[col].duplicated().any()):
                self.df[col] = self.df[col].astype('category')
        return self.df


@dataclass
class DataDiscoverer():
    """
    The DataDiscoverer class provides a data constraints discovery.
    """

    constraints: dict

    def __init__(self, data):
        """Init values"""
        self.data = data
        self.nr_cols = data.select_dtypes(
                include=['number', 'datetime64']
                ).columns
        self.cat_cols = data.select_dtypes(include=['category']).columns
        self.constraints = self.generate_constraints()

    def get_data_type(self, colname: str) -> str:
        """Get column data types"""
        return self.data[colname].dtype

    def is_nullable(self, colname: str) -> bool:
        """Get nullable constraint True/False"""
        return self.data[colname].isna().any()

    def is_unique(self, colname: str) -> bool:
        """Get unique constraint True/False"""
        return ~self.data[colname].duplicated().any()

    def max_length(self, colname: str) -> int:
        """Get max length constraint"""
        return max(self.data[colname].map(len))

    def min_length(self, colname: str) -> int:
        """Get min length constraint"""
        return min(self.data[colname].map(len))

    def value_range(self, colname: str) -> list:
        """Get range of values constraint"""
        return self.data[colname].unique()

    def min_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.data[colname].min()

    def max_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.data[colname].max()

    def generate_constraints(self) -> dict:
        """Generate constraints dict"""
        constraints = {}
        all_cols = self.data.columns
        for col in all_cols:
            constraints[col] = {
                    "data_type": self.get_data_type(col),
                    "nullable": self.is_nullable(col)
                    }
        for col in self.cat_cols:
            constraints[col].update({
                    "unique": self.is_unique(col),
                    "min_length": self.min_length(col),
                    "max_length": self.max_length(col),
                    "value_range": self.value_range(col)
                    })
        for col in self.nr_cols:
            constraints[col].update({
                    "min_value": self.min_value(col),
                    "max_value": self.max_value(col)
                    })
        return constraints

    def modify_constraint(self, column: str,  modify_dict: dict) -> dict:
        """Modify a constrain for a specific column"""
        self.constraints[column].update(modify_dict)
        return self.constraints


@dataclass
class DataVerifier():
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

    def check_data_type(self, constraints: str, colname: str) -> pd.Series:
        """Check data type against constraint"""
        return self.data[colname].dtype == constraints

    def check_nullable(self, constraints: str, colname: str) -> pd.Series:
        """Check null values against constraint"""
        if not constraints:
            nulls = self.data[colname].isna().sum()
        else:
            nulls = 0
        return nulls

    def check_unique(self, constraints: str, colname: str) -> pd.Series:
        """Check duplicate values against constraint"""
        return (~self.data[colname].duplicated().any() != constraints).sum()

    def check_max_length(self, constraints: str, colname: str) -> pd.Series:
        """Check max length against constraint"""
        return (self.data[colname].str.len() > constraints).sum()

    def check_min_length(self, constraints: str, colname: str) -> pd.Series:
        """Check min length against constraint"""
        return (self.data[colname].str.len() < constraints).sum()

    def check_value_range(self, constraints: str, colname: str) -> pd.Series:
        """Check range of values against constraint"""
        return (~self.data[colname].isin(constraints)).sum()

    def check_max_value(self, constraints: str, colname: str) -> pd.Series:
        """Check max value against constraint"""
        if self.data[colname].dtype.kind in "biufc":
            max_val = (self.data[colname] > constraints).sum()
        else:
            max_val = (
                    pd.to_datetime(self.data[colname],
                        infer_datetime_format=True) > constraints
                    ).sum()
        return max_val

    def check_min_value(self, constraints: str, colname: str) -> pd.Series:
        """Check min value against constraint"""
        if self.data[colname].dtype.kind in "biufc":
            min_val = (self.data[colname] < constraints).sum()
        else:
            min_val = (pd.to_datetime(self.data[colname],
                infer_datetime_format=True) < constraints).sum()
        return min_val

    def call_checks(self, check):
        """Map check names with functions"""
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

    def verify_data(self) -> dict:
        """Run all checks for the dataframe"""
        verification = {}
        for col_index, value in self.constraints.items():
            logging.info("Validating %c.", col_index)
            verification[col_index] = {
                    check_key: self.call_checks(check_key)
                    (self.constraints[col_index][check_key], col_index)
                    for check_key, check_value in value.items()
                    }
        return pd.DataFrame(verification).T
