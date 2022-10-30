""" This module contains utility and helper functions"""
import json
import pandas as pd
import numpy as np


def read_file(
    file_path: str, dtypes: dict = None, downcast: bool = False
) -> pd.DataFrame:
    """
    Reads a csv or xlsx file
    Params:
        file_path: str a path to csv or xlsx file
        dtypes: a dictionary of data types
        downcast: a boolean to downcast data types
    Returns:
        A pandas DataFrame
    """

    if ".csv" in file_path:
        frame = pd.read_csv(file_path, dtype=dtypes, sep=",")
    elif ".xlsx" in file_path:
        frame = pd.read_excel(file_path, dtype=dtypes)
    if downcast:
        for col in frame.columns:
            if issubclass(frame[col].dtypes.type, np.int_):
                frame[col] = pd.to_numeric(frame[col], downcast="integer")
            elif issubclass(frame[col].dtypes.type, np.float64):
                frame[col] = pd.to_numeric(frame[col], downcast="float")
            elif issubclass(frame[col].dtypes.type, np.object_) and (
                frame[col].duplicated().any()
            ):
                frame[col] = frame[col].astype("category")
            elif issubclass(frame[col].dtypes.type, np.object_) and (
                frame[col].duplicated().any()
            ):
                frame[col] = frame[col].astype("category")
    return frame


def recast_data_types(frame: pd.DataFrame, dtypes: dict) -> pd.DataFrame:
    """
    Recast data types for a pandas data frame. Tries to parse dates in string or
    unix epoch format.
    Params:
        frame: a pandas DataFrame
        dtypes: a dict of DataFrames columns as kesy and new data type as value.
    Returns:
        A pandas DataFrame with recasted data types.
    """
    non_dates = dict(filter(lambda val: val[1] != "datetime64[ns]", dtypes.items()))
    frame = frame.astype(non_dates)

    dates = dict(filter(lambda val: val[1] == "datetime64[ns]", dtypes.items()))
    for date in dates.keys():
        if frame[date].dtype in [
            int,
            float
        ]:
            unix_date = frame[date].clip(lower=0).astype(str)
            # unix_date = frame[date].astype(int) / 10**9
            unix_date = unix_date.str[:10]
            frame[date] = pd.to_datetime(
                pd.Series(
                    unix_date,
                    dtype="datetime64[ns]",
                ),
                unit="s",
                errors="ignore",
            )
        else:
            frame[date] = pd.to_datetime(
                pd.Series(frame[date], dtype="datetime64[ns]"),
                errors="ignore",
            )
    return frame


class TypeEncoder(json.JSONEncoder):
    """Custom encoder class for json"""
    def default(self, o):
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, set):
            return list(o)
        return super().default(o)
