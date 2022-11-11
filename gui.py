"""GUI interface for frame validation"""
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
import numpy as np
from constraints import StandardConstraints
from verifiers import StandardVerifier
from utils import read_file


sg.theme("DarkBlue2")
sg.set_options(font=("Arial", 12))
ENFORCE_DTYPES = True
STANDARD_HEADINGS = [
    "attribute",
    "data_type",
    "nullable",
    "unique",
    "min_length",
    "max_length",
    "value_range",
    "min_value",
    "max_value",
    "min_date",
    "max_date",
]
CUSTOM_HEADINGS = [
        "name",
        "rule",
        "count"
        ]
DTYPES = [
        "category",
        "bool",
        "float",
        "int",
        "str",
        "datetime64[ns]"
        ]

standard_constraint_properties = [
        [sg.T("attribute: ", key="attribute")],
        [sg.T("data_type: ", size=(11, 1)), sg.Combo(DTYPES, size=(10, 1), key="data_type")],
        [sg.T("nullable: ", size=(11, 1)), sg.Combo([True, False], size=(10, 1), key="nullable")],
        [sg.T("unique: ", size=(11, 1)), sg.Combo([True, False], size=(10, 1), key="unique")],
        [sg.T("min_length: ", size=(11, 1)), sg.I(size=(11, 1), key="min_length")],
        [sg.T("max_length: ", size=(11, 1)), sg.I(size=(11, 1), key="max_length")],
        [sg.T("value_range: ", size=(11, 1)), sg.ML(size=(10, 10), key="value_range")],
        [sg.T("min_value: ", size=(11, 1)), sg.I(size=(11, 1), key="min_value")],
        [sg.T("max_value: ", size=(11, 1)), sg.I(size=(11, 1), key="max_value")],
        [sg.T("min_date: ", size=(11, 1)), sg.I(size=(11, 1), key="min_date")],
        [sg.T("max_date: ", size=(11, 1)), sg.I(size=(11, 1), key="max_date")],
        [sg.P(), sg.B("Update")]
        ]

custom_constraint_properties = [
        [sg.T("name: ", size=(11, 1)), sg.I(size=(20, 1), key="name")],
        [sg.T("query: ", size=(11, 1)), sg.ML(size=(50, 10), key="query")],
        [sg.B("Create"), sg.P(), sg.B("Update")]
        ]

standard_constraints_prop_frame = [[sg.Frame("Standard Contraint Properties", standard_constraint_properties)]]
custom_constraints_prop_frame = [[sg.Frame("Custom Contraint Properties", custom_constraint_properties)]]

def view_constraint_properties(row: pd.DataFrame):
    """
    Opens a GUI window to Modify a single constraint
    Parameters:
        row: a single row pandas DataFrame
    Returns:
        A modified constraints dict and table update
    """
    row_vals = row.to_dict(orient="records")[0]
    for key, _ in row_vals.items():
        window.find_element(key).Update(row_vals[key])
    return row_vals


def update_constraint_properties(row: pd.DataFrame):
    """
    Opens a GUI window to Modify a single constraint
    Parameters:
        row: a single row pandas DataFrame
    Returns:
        A modified constraints dict and table update
    """
    new_vals = row.to_dict(orient="records")[0]
    for key, _ in new_vals.items():
        new_vals[key] = window.find_element(key).Get()
    return new_vals


def view_validation_data(data: pd.DataFrame):
    """
    Opens a GUI window to view the validation break records
    Parameters:
        row: a Verifier.validation_data DataFrame
    Returns:
        A GUI window with table display of breaks
    """
    standard_validation_layout = [
            [[sg.Table(values=data.values.tolist(), headings=data.columns.tolist(), auto_size_columns=False, key="-B_TABLE-", vertical_scroll_only=False, num_rows=20)]],
            [[sg.Button("Close"), sg.Input(visible=False, enable_events=True, key="-SAVE_B_AS-"), sg.FileSaveAs("Save", file_types=(("CSV Files", "*.csv*"),))]]
              ]

    win_width = min(1920, 80 * (len(data.columns)))
    b_window = sg.Window("Modify Constraint",
                         standard_validation_layout,
                         modal=True,
                         size=(win_width, 500))
    while True:
        b_event, b_values = b_window.read()
        if b_event in (sg.WINDOW_CLOSED, "Close"):
            b_window.close()
            break
        if b_event == "-SAVE_B_AS-":
            data.to_csv(b_values["-SAVE_B_AS-"])


standard_layout = [
        [sg.B("Generate Constraints"), sg.B("Recast dtypes"), sg.I(visible=False, enable_events=True, key="-SAVE_C_AS-"), sg.FileSaveAs("Save Constraints"), sg.I(visible=False, enable_events=True, key="-READ_C-"), sg.FileBrowse("Load Constraints")],
        [sg.Table(values=[], headings=STANDARD_HEADINGS, auto_size_columns=False, enable_events=True, key="-C_TABLE-", expand_x=True, num_rows=20)],
        [sg.B("Validate Data"), sg.B("Enforce dtypes", button_color="white on green", key="-DTYPES-"), sg.I(visible=False, enable_events=True, key="-SAVE_V_AS-"), sg.FileSaveAs("Save Summary", file_types=(("CSV Files", "*.csv*"),))],
        [sg.Table(values=[], headings=STANDARD_HEADINGS, auto_size_columns=False, enable_events=True, key="-V_TABLE-", expand_x=True, num_rows=20)],
        [sg.T("Progress: "), sg.ProgressBar(max_value=100, orientation="h", size=(20, 20), key="-PROG-")]
        ]

custom_layout = [
        [sg.B("Create Custom Constraint"), sg.I(visible=False, enable_events=True, key="-SAVE_CUSTOM_AS-"), sg.FileSaveAs("Save Constraints"), sg.I(visible=False, enable_events=True, key="-READ_CUSTOM-"), sg.FileBrowse("Load Constraints")],
        [sg.Table(values=[], headings=CUSTOM_HEADINGS, auto_size_columns=False, enable_events=True, key="-CUSTOM_TABLE-", expand_x=True, num_rows=20)],
        [sg.B("Validate Data"), sg.I(visible=False, enable_events=True, key="-SAVE_CV_AS-"), sg.FileSaveAs("Save Summary", file_types=(("CSV Files", "*.csv*"),))],
        [sg.Table(values=[], headings=CUSTOM_HEADINGS, auto_size_columns=False, enable_events=True, key="-CV_TABLE-", expand_x=True, num_rows=20)],
        [sg.T("Progress: "), sg.ProgressBar(max_value=100, orientation="h", size=(20, 20), key="-CV_PROG-")]]

standard_layout_columns = [
        [sg.Column(standard_layout),
         sg.Column(standard_constraints_prop_frame)]
        ]

custom_layout_columns = [
        [sg.Column(custom_layout),
         sg.Column(custom_constraints_prop_frame)]
        ]

tabgrp = [
        [sg.T("Data File: "), sg.I(enable_events=True, key="-IN-"), sg.FileBrowse(file_types=(("CSV Files", "*.csv*"),))],
        [sg.TabGroup([[sg.Tab("Standard Constraints", standard_layout_columns)],
                      [sg.Tab("Custom Constraints", custom_layout_columns)]]
                     )],
        [sg.Exit()],
        ]

window = sg.Window(
    "Data Validation", tabgrp, modal=True, resizable=True
)


def update_table(headings: list, data: pd.DataFrame) -> pd.DataFrame:
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


def get_constraints_dtypes(constraints: dict) -> dict:
    """Get new data types"""
    new_dtypes = {
        out_key: in_val
        for out_key, out_val in constraints.items()
        for in_key, in_val in out_val.items()
        if in_key == "data_type"
    }
    return new_dtypes


class VerifierProgress(StandardVerifier):
    """Add progress var functionality"""

    data: pd.DataFrame
    constraints: dict
    enforce_dtypes: bool = True

    def __init__(self, data, constraints, enforce_dtypes):
        super().__init__(data, constraints, enforce_dtypes)
        self.validation_summary = self.__validate_data(self.enforce_dtypes)

    def __validate_data(self, enforce_dtypes: bool = False) -> pd.DataFrame:
        """
        Override method to add gui progress bar
        """
        if enforce_dtypes:
            enforced_dtypes = get_constraints_dtypes(self.constraints)
            self.data = self.data.astype(enforced_dtypes)

        verification = {}
        progress = 0
        nr_cols = len(self.data.columns)
        for col_index, value in self.constraints.items():
            progress += 100 / nr_cols
            window["-PROG-"].Update(progress)
            # pylint: disable=duplicate-code
            verification[col_index] = {
                check_key: self._call_checks(check_key)(
                    self.constraints[col_index][check_key], col_index
                )
                for check_key, check_value in value.items()
            }
        return pd.DataFrame(verification)


# Main loop
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "-IN-":
        if Path(values["-IN-"]).exists():
            frame = read_file(values["-IN-"], downcast=True)
        else:
            sg.PopupError("File Path does not exists")
    if "frame" in locals():
        if event == "Generate Constraints":
            const = StandardConstraints()
            const.generate_constraints(frame)
            c_update = update_table(STANDARD_HEADINGS, const.constraints)
            window["-C_TABLE-"].Update(c_update.values.tolist())

        if event == "-C_TABLE-":
            t_data_index = values["-C_TABLE-"]
            if len(t_data_index) > 0:
                row_data = c_update.filter(items=t_data_index, axis=0)
                view_constraint_properties(row_data)

        if event == "Update":
            new_values = update_constraint_properties(row_data)
            mod = {
                    k: v for k, v in new_values.items() if v not in ["nan", "NaN"]
                    }
            dtype_mapping = {
                    "attribute": str,
                    "data_type": str,
                    "nullable": bool,
                    "unique": bool,
                    "min_length": lambda i: int(float(i)),
                    "max_length": lambda i: int(float(i)),
                    "value_range": lambda i: set(
                        map(str.strip, i.strip("}{").replace("'", "").split(","))
                        ),
                    "min_value": float,
                    "max_value": float,
                    "min_date": str,
                    "max_date": str,
                    }
            mod = {
                    key: dtype_mapping.get(key)(value)
                    for key, value in mod.items()
                    }
            del mod["attribute"]
            const.modify_constraint(new_values["attribute"], mod)
            m_update = update_table(STANDARD_HEADINGS, const.constraints)
            window["-C_TABLE-"].Update(m_update.values.tolist())
          
        if event == "Recast dtypes":
            dtypes = get_constraints_dtypes(const.constraints)
            frame = read_file(values["-IN-"], downcast=True, dtypes=dtypes)
            const.generate_constraints(frame)
            c_update = update_table(STANDARD_HEADINGS, const.constraints)
            window["-C_TABLE-"].Update(c_update.values.tolist())
        if event == "-DTYPES-":
            ENFORCE_DTYPES = not ENFORCE_DTYPES
            window["-DTYPES-"].update(
                button_color="white on green"
                if ENFORCE_DTYPES
                else "white on red"
            )
        if event == "Validate Data":
            try:
                valid = VerifierProgress(
                    frame, const.constraints, ENFORCE_DTYPES
                )
                v_update = update_table(STANDARD_HEADINGS,
                                        valid.validation_summary)
                v_update = v_update.infer_objects()
                v_update = v_update.loc[
                    v_update.sum(axis=1, numeric_only=True) >= 1
                ].reset_index(drop=True)
                window["-V_TABLE-"].Update(v_update.values.tolist())
            except KeyError as v:
                sg.Popup(f"Constraint for {v} but {v} not in data")
    else:
        sg.PopupError("No Data is loaded")

    if event == "-V_TABLE-":
        t_data_index = values["-V_TABLE-"]
        row_data = v_update.filter(items=t_data_index, axis=0)
        if len(row_data) > 0:
            row_data = row_data.to_dict(orient="records")[0]
            validation_data = valid.validation_data[
                valid.validation_data["Validation"].str.contains(
                    row_data["attribute"]
                )
            ]
            view_validation_data(validation_data)

    # Loading and saving events
    if event == "-SAVE_C_AS-":
        const.save_as(values["-SAVE_C_AS-"])
    if event == "-READ_C-":
        const = StandardConstraints()
        const.read_constraints(values["-READ_C-"])
        c_update = update_table(STANDARD_HEADINGS, const.constraints)
        window["-C_TABLE-"].Update(c_update.values.tolist())
    if event == "-SAVE_V_AS-":
        valid.validation_summary.T.to_csv(values["-SAVE_V_AS-"])

window.close()
