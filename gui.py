""" GUI interface for DataFrame validation """
import PySimpleGUI as sg
import pandas as pd
import numpy as np
from dataparser import DataParser
from constraints import Constraints
from verifier import Verifier


sg.theme("DarkBlue2")
sg.set_options(font=("Arial", 12))


def generate_constraints(file_path: str) -> Constraints:
    """
    Generate constraints from file

    Parameters:
        file_path: a file path string
    Returns:
        A Constraints object
    """
    frame = pd.read_csv(file_path)
    data = DataParser(frame)
    del frame
    data_constraints = Constraints()
    data_constraints.generate_constraints(data.data)
    return data_constraints


def validate_data(file_path: str, constraints: Constraints) -> Verifier:
    """
    Validates a dataframe from file
    Parameters:
        file_path: a file path string
        constraints: a Constraints object
    Returns:
        A Verifier object
    """
    frame = pd.read_csv(file_path)
    data = DataParser(frame)
    del frame
    verifier = Verifier(data.data, constraints.constraints)
    return verifier


def modify_constraint(row: pd.DataFrame):
    """
    Open a GUI window to Modify a single constraint
    Parameters:
        row: a single row pandas DataFrame
    """
    attribute = row["attribute"].values[0]
    nullable = row["nullable"].values[0]
    unique = row["unique"].values[0]
    min_length = row["min_length"].values[0]
    max_length = row["max_length"].values[0]
    value_range = row["value_range"].values[0]
    min_value = row["min_value"].values[0]
    max_value = row["max_value"].values[0]
    min_date = row["min_date"].values[0]
    max_date = row["max_date"].values[0]

    mod_layout = [
            [[sg.Text(f"Attribute: {attribute}")]],
            [
                [sg.Text("nullable: ", size=(11, 1)),
                 sg.Combo([True, False], nullable, size=(10, 1))]
                ],
            [
                [sg.Text("unique: ", size=(11, 1)),
                 sg.Combo([True, False], unique,  size=(10, 1))]
                ],
            [
                [sg.Text("min_length: ", size=(11, 1)),
                 sg.Input(min_length, size=(11, 1))]
                ],
            [
                [sg.Text("max_length: ", size=(11, 1)),
                 sg.Input(max_length, size=(11, 1))]
                ],
            [
                [sg.Text("value_range: ", size=(11, 1)),
                 sg.Multiline(value_range, size=(11, 5))]
                ],
            [
                [sg.Text("min_value: ", size=(11, 1)),
                 sg.Input(min_value, size=(11, 1))]
                ],
            [
                [sg.Text("max_value: ", size=(11, 1)),
                 sg.Input(max_value, size=(11, 1))]
                ],
            [
                [sg.Text("min_date: ", size=(11, 1)),
                 sg.Input(min_date, size=(11, 1))]
                ],
            [
                [sg.Text("max_date: ", size=(11, 1)),
                 sg.Input(max_date, size=(11, 1))]
                ],
            [sg.Button("Close"), sg.Push(), sg.Button("Submit")]
            ]
    mod_window = sg.Window("Modify Contraint", mod_layout, modal=True)
    while True:
        mod_event, mod_values = mod_window.read()
        if event in (sg.WINDOW_CLOSED, "Close"):
            mod_window.close()


HEADINGS = ["attribute", "data_type", "nullable", "unique", "min_length",
            "max_length", "value_range", "min_value", "max_value", "min_date",
            "max_date"]

layout1 = [
        [sg.Button("Generate Constraints")],
        [sg.Table(values=[],
                  headings=HEADINGS,
                  auto_size_columns=False,
                  enable_events=True,
                  key="-C_TABLE-",
                  expand_x=True,
                  num_rows=20
                  )
         ],
        [sg.Button("Validate Data")],
        [sg.Table(values=[],
                  headings=HEADINGS,
                  auto_size_columns=False,
                  key="-V_TABLE-",
                  expand_x=True,
                  num_rows=20
                  )
         ],
            ]
layout2 = []

tabgrp = [
        [sg.Text("Data:"), sg.Input(key="-IN-"),
         sg.FileBrowse(file_types=(("CSV Files", "*.csv*"),))],
        [sg.TabGroup([
            [sg.Tab("Validation", layout1)],
            [sg.Tab("Profile", layout2)]
            ], size=(1920, 900))],
        [sg.Exit()]
        ]

window = sg.Window("Data Validation",
                   tabgrp, modal=True,
                   size=(1920, 1080),
                   resizable=True)


def update_table(headings: list, constraints: dict) -> pd.DataFrame:
    """
    Update GUI validation tables
    Parameters:
        headings: a list of column names
        data: a constraints dict
    Returns:
        An updated pandas DataFrame
    """
    cols = pd.DataFrame(columns=headings)
    t_data = pd.DataFrame(constraints).T.reset_index()
    t_data.rename(columns={"index": "attribute"}, inplace=True)
    t_data.fillna(np.NaN, inplace=True)
    # t_data = t_data.loc[t_data.sum(axis=1, numeric_only=True) >= 1]
    t_update = pd.concat([cols, t_data])
    return t_update


while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "Generate Constraints":
        const = generate_constraints(file_path=values["-IN-"])
        update = update_table(HEADINGS, const.constraints)
        window["-C_TABLE-"].Update(update.values.tolist())
    if event == "Validate Data":
        try:
            valid = validate_data(file_path=values["-IN-"], constraints=const)
            update = update_table(HEADINGS, valid.validation_summary.T)
            window["-V_TABLE-"].Update(update.values.tolist())
        except ValueError as v:
            sg.Popup(f"Constraint for {v} but {v} not in data")
    if event == "-C_TABLE-":
        t_data_index = values["-C_TABLE-"]
        row_data = update.filter(items=t_data_index, axis=0)
        modify_constraint(row_data)
        window.close()
