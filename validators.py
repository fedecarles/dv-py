import datetime as datetime
import pandas as pd


class DataDiscoverer():

    constraints: dict

    def __init__(self, df):
        self.df = df
        self._guess_date_types(df)

        self.nr_cols = df.select_dtypes(
                include=['int64', 'float64', 'datetime64']
                ).columns
        self.str_cols = df.select_dtypes(include=[object]).columns

    def _guess_date_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convert date columns to datetime"""
        dt_cols = data.filter(
                regex='Fecha|date|dt|DT|Date|maturity|EROD'
                ).columns
        for dt in dt_cols:
            data[dt] = pd.to_datetime(
                    data[dt],
                    errors='ignore', 
                    infer_datetime_format=True)
        return data

    def get_data_type(self, colname: str) -> str:
        """Get column data types"""
        return self.df[colname].dtype

    def is_nullable(self, colname: str) -> bool:
        """Get nullable constraint True/False"""
        return self.df[colname].isna().any()

    def is_unique(self, colname: str) -> bool:
        """Get unique constraint True/False"""
        return ~self.df[colname].duplicated().any()

    def max_length(self, colname: str) -> int:
        """Get max length constraint"""
        return max([len(i) for i in self.df[colname]])

    def min_length(self, colname: str) -> int:
        """Get min length constraint"""
        return min([len(i) for i in self.df[colname]])

    def value_range(self, colname: str) -> list:
        """Get range of values constraint"""
        return self.df[colname].unique()

    def min_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.df[colname].min()

    def max_value(self, colname: str) -> float:
        """Get min value constraint"""
        return self.df[colname].max()

    def generate_constraints(self) -> dict:
        """Generate constraints dict"""
        constraints = {}
        all_cols = self.df.columns
        for c in all_cols:
            constraints[c] = {
                    "data_type":self.get_data_type(c),
                    "nullable": self.is_nullable(c)
                    }
        for c in self.str_cols:
            constraints[c].update({
                    "unique": self.is_unique(c),
                    "min_length": self.min_length(c),
                    "max_length": self.max_length(c),
                    "value_range": self.value_range(c)
                    })
        for c in self.nr_cols:
            constraints[c].update({
                    "min_value": self.min_value(c),
                    "max_value": self.max_value(c)
                    })
        return constraints
        
class DataVerifier():
    def __init__(self, data: pd.DataFrame, constraints: dict):
        self.constraints = constraints
        self.data = data

    def check_data_type(self, constraints: str, colname: str) -> pd.Series:
        """Check data type against constraint"""
        return self.data[colname].dtype == constraints

    def check_nullable(self, constraints: str, colname: str) -> pd.Series:
        """Check null values against constraint"""
        return (self.data[colname].isna() != constraints).sum()

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
        if self.data[colname].dtype in [int, float]:
            e = (self.data[colname] > constraints).sum()
        else:
            e = (pd.to_datetime(self.data[colname],
                infer_datetime_format=True) > constraints).sum()
        return e

    def check_min_value(self, constraints: str, colname: str) -> pd.Series:
        """Check min value against constraint"""
        if self.data[colname].dtype in [int, float]:
            e = (self.data[colname] < constraints).sum()
        else:
            e = (pd.to_datetime(self.data[colname],
                infer_datetime_format=True) < constraints).sum()
        return e

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
        d = {}
        for ix, val in self.constraints.items():
            d[ix] = dict(
                    [(k, self.call_checks(k)(self.constraints[ix][k], ix))
                        for k, v in val.items() if k==k
                    ])
        return pd.DataFrame(d).T
