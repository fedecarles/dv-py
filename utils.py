# pylint: skip-file
""" This module contains utility and helper functions"""
import json
import pandas as pd
import numpy as np


def read_file(
    file_path: str, dtypes: dict = None, downcast: bool = False
) -> pd.DataFrame:
    """
    Reads a csv or xlsx file
    :param file_path: an str path to csv or xlsx file
    :param dtypes: a dictionary of data types
    :param downcast: a boolean to downcast data types
    :returns: a DataFrame
    """
    if dtypes:
        non_dates = dict(
            filter(lambda val: val[1] != "datetime64[ns]", dtypes.items())
        )
        dates = dict(
            filter(lambda val: val[1] == "datetime64[ns]", dtypes.items())
        )
    else:
        non_dates = {}
        dates = {}

    if ".csv" in file_path:
        frame = pd.read_csv(file_path, dtype=non_dates, sep=",")
    elif ".xlsx" in file_path:
        frame = pd.read_excel(file_path, dtype=non_dates)

    for date in dates.keys():
        if pd.api.types.is_numeric_dtype(frame[date]):
            unix_date = frame[date].clip(lower=0).astype(str)
            unix_date = unix_date.str[:10]
            frame[date] = pd.to_datetime(
                pd.Series(unix_date, dtype="datetime64[ns]"),
                unit="s",
                errors="ignore",
            )
        else:
            frame[date] = pd.to_datetime(
                pd.Series(frame[date], dtype="datetime64[ns]"), errors="ignore"
            )

    if downcast:
        for col in frame.columns:
            if issubclass(frame[col].dtypes.type, np.int_):
                frame[col] = pd.to_numeric(frame[col], downcast="integer")
            elif issubclass(frame[col].dtypes.type, np.float64):
                frame[col] = pd.to_numeric(frame[col], downcast="float")
            elif issubclass(frame[col].dtypes.type, np.object_) and (
                len(frame[col].unique()) <= 20
            ):
                frame[col] = frame[col].astype("category")
            elif issubclass(frame[col].dtypes.type, np.object_) and (
                len(frame[col].unique()) > 20
            ):
                frame[col] = frame[col].astype(str)
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
