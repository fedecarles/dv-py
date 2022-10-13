"""This module provides the basic objects for the dataframe-validation"""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class DataParser:
    """
    The DataParser class contains functions to optimize and
    prepare a pandas DataFrame

    Attributes:
        data: pd.Dataframe
    """
    data: pd.DataFrame()

    def __post_init__(self):
        """Init values"""
        self._optimize_dtypes()
        self._guess_date_types()

    def _guess_date_types(self) -> pd.DataFrame:
        """
        Attempt to guess date columns by name and converts to datetime.

        Parameters:
            data: A pandas DataFrame
        Returns:
            A pandas DataFrame with date columns as datetime64
        """
        date_cols = self.data.filter(
                regex='Fecha|date|dt|DT|Date|DATE|maturity|EROD'
                ).columns
        for date in date_cols:
            self.data[date] = pd.to_datetime(
                    self.data[date],
                    errors='ignore',
                    infer_datetime_format=True).astype('datetime64[ns]')
        return self.data

    def _optimize_dtypes(self) -> pd.DataFrame:
        """
        Optimizes data types.

        Parameters:
            data: A pandas DataFrame
        Returns:
            A pandas DataFrame with data types downcasted.
        """
        for col in self.data.columns:
            if issubclass(self.data[col].dtypes.type, np.int_):
                self.data[col] = pd.to_numeric(
                        self.data[col],
                        downcast='integer'
                        )
            elif issubclass(self.data[col].dtypes.type, np.float64):
                self.data[col] = pd.to_numeric(
                        self.data[col],
                        downcast='float'
                        )
            elif issubclass(self.data[col].dtypes.type, np.object_) \
                    and (self.data[col].duplicated().any()):
                self.data[col] = self.data[col].astype('category')
        return self.data
