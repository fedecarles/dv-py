import pandas as pd


class DataDiscoverer():
    """
    The DataDiscoverer class provides a data constraints discovery.
    """

    constraints: dict

    def __init__(self, data):
        self.data = data
        self._guess_date_types(data)

        self.nr_cols = data.select_dtypes(
                include=['int64', 'float64', 'datetime64']
                ).columns
        self.str_cols = data.select_dtypes(include=[object]).columns

    def _guess_date_types(self) -> pd.DataFrame:
        """Convert date columns to datetime"""
        date_cols = self.data.filter(
                regex='Fecha|date|dt|DT|Date|maturity|EROD'
                ).columns
        for date in date_cols:
            self.data[date] = pd.to_datetime(
                    self.data[date],
                    errors='ignore',
                    infer_datetime_format=True)
        return self.data

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
        return max([len(i) for i in self.data[colname]])

    def min_length(self, colname: str) -> int:
        """Get min length constraint"""
        return min([len(i) for i in self.data[colname]])

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
                    "data_type":self.get_data_type(col),
                    "nullable": self.is_nullable(col)
                    }
        for col in self.str_cols:
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

class DataVerifier():
    """
    The DataVerifier class provides a way to verify constraints on a 
    dataframe.
    """

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
            max_val = (self.data[colname] > constraints).sum()
        else:
            max_val = (pd.to_datetime(self.data[colname],
                infer_datetime_format=True) > constraints).sum()
        return max_val

    def check_min_value(self, constraints: str, colname: str) -> pd.Series:
        """Check min value against constraint"""
        if self.data[colname].dtype in [int, float]:
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
            verification[col_index] = dict(
                    [(check_key, self.call_checks(check_key)
                        (self.constraints[col_index][check_key], col_index))
                        for check_key, check_value in value.items() if check_key
                    ])
        return pd.DataFrame(verification).T
