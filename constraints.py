"""This module provides the basic objects for the dataframe_validation"""

from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Constraints():
    """
    The Constraints class provides a data constraints discovery.
    """

    constraints: dict = field(default_factory=dict)

    def get_data_type(self, data: pd.DataFrame, colname: str) -> str:
        """Get column data types"""
        return data[colname].dtype.name

    def is_nullable(self, data: pd.DataFrame, colname: str) -> bool:
        """Get nullable constraint True/False"""
        return data[colname].isna().any()

    def is_unique(self, data: pd.DataFrame, colname: str) -> bool:
        """Get unique constraint True/False"""
        return ~data[colname].duplicated().any()

    def max_length(self, data: pd.DataFrame, colname: str) -> int:
        """Get max length constraint"""
        return max(data[colname].map(str).map(len))

    def min_length(self, data: pd.DataFrame, colname: str) -> int:
        """Get min length constraint"""
        return min(data[colname].map(str).map(len))

    def value_range(self, data: pd.DataFrame, colname: str) -> list:
        """Get range of values constraint"""
        return data[colname].unique().categories.to_list()

    def min_value(self, data: pd.DataFrame, colname: str) -> float:
        """Get min value constraint"""
        return data[colname].min()

    def max_value(self, data: pd.DataFrame, colname: str) -> float:
        """Get min value constraint"""
        return data[colname].max()

    def min_date(self, data: pd.DataFrame, colname: str) -> pd.datetime:
        """Get min value constraint"""
        return data[colname].min().strftime("%Y-%m-%d")

    def max_date(self, data: pd.DataFrame, colname: str) -> pd.datetime:
        """Get min value constraint"""
        return data[colname].max().strftime("%Y-%m-%d")

    def generate_constraints(self, data: pd.DataFrame) -> dict:
        """Generate constraints dict"""
        all_cols = data.columns
        nr_cols = data.select_dtypes(include=['number']).columns
        cat_cols = data.select_dtypes(include=['category']).columns
        dt_cols = data.select_dtypes(include=['datetime64']).columns

        for col in all_cols:
            self.constraints[col] = {
                    "data_type": self.get_data_type(data, col),
                    "nullable": self.is_nullable(data, col)
                    }
        for col in cat_cols:
            self.constraints[col].update({
                    "unique": self.is_unique(data, col),
                    "min_length": self.min_length(data, col),
                    "max_length": self.max_length(data, col),
                    "value_range": self.value_range(data, col)
                    })
        for col in nr_cols:
            self.constraints[col].update({
                    "min_value": self.min_value(data, col),
                    "max_value": self.max_value(data, col)
                    })
        for col in dt_cols:
            self.constraints[col].update({
                    "min_date": self.min_date(data, col),
                    "max_date": self.max_date(data, col)
                    })
        return self.constraints

    def modify_constraint(self, column: str,  modify_dict: dict) -> dict:
        """Modify a constrain for a specific column"""
        self.constraints[column].update(modify_dict)
        return self.constraints
