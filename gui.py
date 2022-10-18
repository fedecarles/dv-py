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
    Opens a GUI window to Modify a single constraint
    Parameters:
        row: a single row pandas DataFrame
    Returns:
        A modified constraints dict and table update
    """
    m_vals = row.to_dict(orient='records')[0]
    d_types = ['category', "bool", "float"]

    mod_layout = [
            [[sg.Text(f"Attribute: {m_vals['attribute']}")]],
            [
                [sg.Text("data_type: ", size=(11, 1)),
                 sg.Combo(d_types, m_vals["data_type"],
                          size=(10, 1), key="data_type")]
                ],
            [
                [sg.Text("nullable: ", size=(11, 1)),
                 sg.Combo([True, False], str(m_vals["nullable"]),
                          size=(10, 1), key="nullable")]
                ],
            [
                [sg.Text("unique: ", size=(11, 1)),
                 sg.Combo([True, False], m_vals["unique"],
                          size=(10, 1), key="unique")]
                ],
            [
                [sg.Text("min_length: ", size=(11, 1)),
                 sg.Input(m_vals["min_length"],
                          size=(11, 1), key="min_length")]
                ],
            [
                [sg.Text("max_length: ", size=(11, 1)),
                 sg.Input(m_vals["max_length"],
                          size=(11, 1), key="max_length")]
                ],
            [
                [sg.Text("value_range: ", size=(11, 1)),
                 sg.Multiline(m_vals["value_range"],
                              size=(10, 5), key="value_range")]
                ],
            [
                [sg.Text("min_value: ", size=(11, 1)),
                 sg.Input(m_vals["min_value"],
                          size=(11, 1), key="min_value")]
                ],
            [
                [sg.Text("max_value: ", size=(11, 1)),
                 sg.Input(m_vals["max_value"],
                          size=(11, 1), key="max_value")]
                ],
            [
                [sg.Text("min_date: ", size=(11, 1)),
                 sg.Input(m_vals["min_date"],
                          size=(11, 1), key="min_date")]
                ],
            [
                [sg.Text("max_date: ", size=(11, 1)),
                 sg.Input(m_vals["max_date"],
                          size=(11, 1), key="max_date")]
                ],
            [sg.Button("Close"), sg.Push(), sg.Button("Submit")]
            ]
    mod_window = sg.Window("Modify Constraint", mod_layout, modal=True)
    while True:
        mod_event, mod_values = mod_window.read()
        if mod_event == "Submit":
            mod = {k: v for k, v in mod_values.items()
                   if v not in ['nan', 'NaN']}
            dtype_mapping = {
                    "data_type": str,
                    "nullable": bool,
                    "unique": bool,
                    "min_length": lambda i: int(float(i)),
                    "max_length": lambda i: int(float(i)),
                    "value_range": lambda i: list(
                        map(
                            str.strip, i.strip("][").replace("'", "").split(
                                ","
                                ))
                            ),
                    "min_value": float,
                    "max_value": float,
                    "min_date": str,
                    "max_date": str
                    }
            mod = {key: dtype_mapping.get(key)(value)
                   for key, value in mod.items()}
            const.modify_constraint(m_vals["attribute"], mod)
            m_update = update_table(HEADINGS, const.constraints)
            window["-C_TABLE-"].Update(m_update.values.tolist())

        if mod_event in (sg.WINDOW_CLOSED, "Close"):
            mod_window.close()
            break


def view_validation_data(data: pd.DataFrame):
    """
    Opens a GUI window to view the validation break records
    Parameters:
        row: a Verifier.validation_data DataFrame
    Returns:
        A GUI window with table display of breaks
    """
    b_layout = [
            [[sg.Table(values=data.values.tolist(),
                       headings=data.columns.tolist(),
                       auto_size_columns=False,
                       key="-B_TABLE-",
                       vertical_scroll_only=False,
                       num_rows=20
                       )
              ]],
            [[sg.Button("Close")]]
            ]
    b_window = sg.Window("Modify Constraint", b_layout, modal=True,
                         size=(1920, 500))
    while True:
        b_event, b_values = b_window.read()
        if b_event in (sg.WINDOW_CLOSED, "Close"):
            b_window.close()
            break


HEADINGS = ["attribute", "data_type", "nullable", "unique", "min_length",
            "max_length", "value_range", "min_value", "max_value", "min_date",
            "max_date"]

layout1 = [
        [sg.Button("Generate Constraints"),
         sg.Input(visible=False, enable_events=True, key="-SAVE_C_AS-"),
         sg.FileSaveAs("Download Constraints")],
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
                  enable_events=True,
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
            [sg.Tab("Standard Constraints", layout1)],
            [sg.Tab("Custom Constraints", layout2)]
            ], size=(1920, 900))],
        [sg.Exit()]
        ]

window = sg.Window("Data Validation",
                   tabgrp, modal=True,
                   size=(1920, 1080),
                   resizable=True)


def update_table(headings: list, data: pd.DataFrame, ) -> pd.DataFrame:
    """
    Update GUI validation tables
    Parameters:
        headings: a list of column names
        data: a constraints dict
    Returns:
        An updated pandas DataFrame
    """
    cols = pd.DataFrame(columns=headings)
    t_data = pd.DataFrame(data).T.reset_index()
    t_data.rename(columns={"index": "attribute"}, inplace=True)
    t_data.fillna(np.NaN, inplace=True)
    t_update = pd.concat([cols, t_data])
    return t_update


while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "Generate Constraints":
        const = generate_constraints(file_path=values["-IN-"])
        c_update = update_table(HEADINGS, const.constraints)
        window["-C_TABLE-"].Update(c_update.values.tolist())
    if event == "-SAVE_C_AS-":
        const.save_as(values["-SAVE_C_AS-"])
    if event == "Validate Data":
        try:
            valid = validate_data(file_path=values["-IN-"], constraints=const)
            v_update = update_table(HEADINGS, valid.validation_summary)
            # v_update = v_update.loc[
            #         v_update.sum(axis=1, numeric_only=True) >= 1
            #         ]
            window["-V_TABLE-"].Update(v_update.values.tolist())
        except ValueError as v:
            sg.Popup(f"Constraint for {v} but {v} not in data")
    if event == "-C_TABLE-":
        t_data_index = values["-C_TABLE-"]
        if len(t_data_index) > 0:
            row_data = c_update.filter(items=t_data_index, axis=0)
            modify_constraint(row_data)
    if event == "-V_TABLE-":
        t_data_index = values["-V_TABLE-"]
        row_data = v_update.filter(items=t_data_index, axis=0)
        if len(row_data) > 0:
            row_data = row_data.to_dict(orient='records')[0]
            validation_data = valid.validation_data[
                    valid.validation_data["Validation"].str.contains(
                        row_data["attribute"]
                        )
                    ]
            view_validation_data(validation_data)
window.close()
