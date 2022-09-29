"""This module provides the basic objects for the dataframe-validation"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class Constraints():
    """
    The Constraints class provides a data constraints discovery.
    """

    data: pd.DataFrame

    def __post_init__(self):
        """Post init values"""
        self.nr_cols = self.data.select_dtypes(
                include=['number', 'datetime64']
                ).columns
        self.cat_cols = self.data.select_dtypes(include=['category']).columns
        self.constraints = self.__generate_constraints()

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
        return max(self.data[colname].map(str).map(len))

    def min_length(self, colname: str) -> int:
        """Get min length constraint"""
        return min(self.data[colname].map(str).map(len))

    def value_range(self, colname: str) -> list:
        """Get range of values constraint"""
        return self.data[colname].unique()

    def min_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.data[colname].min()

    def max_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.data[colname].max()

    def __generate_constraints(self) -> dict:
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
