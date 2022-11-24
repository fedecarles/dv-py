"""GUI interface for frame validation"""
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
import numpy as np
from constraints import StandardConstraints, CustomConstraints
from verifiers import StandardVerifier, CustomVerifier
from utils import read_file
from layouts import STANDARD_HEADINGS, tabgrp


def view_constraint_properties(row: pd.DataFrame):
    """
    Opens a GUI window to Modify a single constraint
    :param row: a single row pandas DataFrame
    :return: a modified constraints dict and table update
    """
    row_vals = row.to_dict(orient="records")[0]
    for key, _ in row_vals.items():
        window.find_element(key).Update(row_vals[key])
    return row_vals


def update_constraint_properties(row: pd.DataFrame):
    """
    Opens a GUI window to Modify a single constraint
    :param row: a single row pandas DataFrame
    :return: a modified constraints dict and table update
    """
    new_vals = row.to_dict(orient="records")[0]
    for key, _ in new_vals.items():
        new_vals[key] = window.find_element(key).Get()
    return new_vals


def view_validation_data(data: pd.DataFrame):
    """
    Opens a GUI window to view the validation break records
    :param row: a Verifier.validation_data DataFrame
    :return: a GUI window with table display of breaks
    """
    standard_validation_layout = [
        [
            [
                sg.Table(
                    values=data.values.tolist(),
                    headings=data.columns.tolist(),
                    auto_size_columns=False,
                    key="-B_TABLE-",
                    vertical_scroll_only=False,
                    num_rows=20,
                )
            ]
        ],
        [
            [
                sg.Button("Close"),
                sg.Input(visible=False, enable_events=True, key="-SAVE_B_AS-"),
                sg.FileSaveAs("Save", file_types=(("CSV Files", "*.csv*"),)),
            ]
        ],
    ]

    win_width = min(1920, 80 * (len(data.columns)))
    b_window = sg.Window(
        "Modify Constraint",
        standard_validation_layout,
        modal=True,
        size=(win_width, 500),
    )
    while True:
        b_event, b_values = b_window.read()
        if b_event in (sg.WINDOW_CLOSED, "Close"):
            b_window.close()
            break
        if b_event == "-SAVE_B_AS-":
            data.to_csv(b_values["-SAVE_B_AS-"])


window = sg.Window("Data Validation", tabgrp, modal=True, resizable=True)


def update_table(headings: list, data: pd.DataFrame) -> pd.DataFrame:
    """
    Update GUI validation tables
    :param headings: a list of column names
    :param data: a constraints dict
    :return: an updated pandas DataFrame
    """
    cols = pd.DataFrame(columns=headings)
    t_data = pd.DataFrame(data).T.reset_index()
    t_data.rename(columns={"index": "attribute"}, inplace=True)
    t_data.fillna(np.NaN, inplace=True)
    t_update = pd.concat([cols, t_data])
    return t_update


def get_constraints_dtypes(constraints: dict) -> dict:
    """
    Get new constraints data types
    :param Constraints object
    :return: dictionary of new data types
    """
    new_dtypes = {
        out_key: in_val
        for out_key, out_val in constraints.items()
        for in_key, in_val in out_val.items()
        if in_key == "data_type"
    }
    return new_dtypes


class VerifierProgress(StandardVerifier):
    """
    Overrides StandardVerifier validation function to
    incorporate GUI progress bar functionality
    """

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
def main():
    "Main GUI loop"

    enforce_dtypes = True

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
                t_update = update_table(STANDARD_HEADINGS, const.constraints)
                window["-STANDARD_TABLE-"].Update(t_update.values.tolist())

            if event == "-STANDARD_TABLE-":
                t_data_index = values["-STANDARD_TABLE-"]
                if len(t_data_index) > 0:
                    row_data = t_update.filter(items=t_data_index, axis=0)
                    view_constraint_properties(row_data)

            if event == "Update":
                new_values = update_constraint_properties(row_data)
                mod = {
                    k: v
                    for k, v in new_values.items()
                    if v not in ["nan", "NaN"]
                }
                dtype_mapping = {
                    "attribute": str,
                    "data_type": str,
                    "nullable": bool,
                    "unique": bool,
                    "min_length": lambda i: int(float(i)),
                    "max_length": lambda i: int(float(i)),
                    "value_range": lambda i: set(
                        map(
                            str.strip,
                            i.strip("}{").replace("'", "").split(","),
                        )
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
                t_update = update_table(STANDARD_HEADINGS, const.constraints)
                window["-STANDARD_TABLE-"].Update(t_update.values.tolist())

            if event == "Recast dtypes":
                dtypes = get_constraints_dtypes(const.constraints)
                frame = read_file(values["-IN-"], downcast=True, dtypes=dtypes)
                const.generate_constraints(frame)
                t_update = update_table(STANDARD_HEADINGS, const.constraints)
                window["-STANDARD_TABLE-"].Update(t_update.values.tolist())
            if event == "-DTYPES-":
                enforce_dtypes = not enforce_dtypes
                window["-DTYPES-"].update(
                    button_color="white on green"
                    if enforce_dtypes
                    else "white on red"
                )
            if event == "Validate Data":
                try:
                    valid = VerifierProgress(
                        frame, const.constraints, enforce_dtypes
                    )
                    v_update = update_table(
                        STANDARD_HEADINGS, valid.validation_summary
                    )
                    v_update = v_update.infer_objects()
                    v_update = v_update.loc[
                        v_update.sum(axis=1, numeric_only=True) >= 1
                    ].reset_index(drop=True)
                    window["-V_TABLE-"].Update(v_update.values.tolist())
                except KeyError as ke:
                    sg.Popup(f"Constraint for {ke} but {ke} not in data")
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

        # Custom constraints
        if event == "Create":
            if "custom_constraints" not in locals():
                custom_constraints = CustomConstraints()
                custom_constraints.add_custom_constraint(
                    values["-NAME-"], values["-QUERY-"]
                )
            else:
                custom_constraints.add_custom_constraint(
                    values["-NAME-"], values["-QUERY-"]
                )
            all_custom_constraints = (
                custom_constraints.view_custom_constraints()
            )
            window["-CUSTOM_TABLE-"].Update(
                all_custom_constraints.values.tolist()
            )

        if event == "-CUSTOM_TABLE-":
            t_data_index = values["-CUSTOM_TABLE-"]
            if len(t_data_index) > 0:
                ct_update = update_table(
                    ["name", "query"], all_custom_constraints.T
                )
                row_data = ct_update.filter(items=t_data_index, axis=0)
                window["-NAME-"].Update(row_data["name"].values[0])
                window["-QUERY-"].Update(row_data["query"].values[0])

        if event == "Delete":
            custom_constraints.delete_custom_constraint(values["-NAME-"])
            all_custom_constraints = (
                custom_constraints.view_custom_constraints()
            )
            window["-CUSTOM_TABLE-"].Update(
                all_custom_constraints.values.tolist()
            )

        if event == "Validate Custom":
            custom_verify = CustomVerifier(
                    frame, custom_constraints.custom_constraints
                    )
            window["-CV_TABLE-"].Update(
                custom_verify.validation_summary.values.tolist()
            )

        if event == "-CV_TABLE-":
            t_data_index = values["-CV_TABLE-"]
            row_data = custom_verify.validation_summary.filter(
                items=t_data_index, axis=0
            )
            if len(row_data) > 0:
                row_data = row_data.to_dict(orient="records")[0]
                validation_data = custom_verify.validation_data[
                    custom_verify.validation_data["Validation"].str.contains(
                        row_data["name"]
                    )
                ]
                view_validation_data(validation_data)

        # Loading and saving events
        if event == "-SAVE_C_AS-":
            const.save_as(values["-SAVE_C_AS-"])
        if event == "-READ_C-":
            const = StandardConstraints()
            const.read_constraints(values["-READ_C-"])
            t_update = update_table(STANDARD_HEADINGS, const.constraints)
            window["-STANDARD_TABLE-"].Update(t_update.values.tolist())
        if event == "-SAVE_V_AS-":
            valid.validation_summary.T.to_csv(values["-SAVE_V_AS-"])

        if event == "-SAVE_CUSTOM_AS-":
            custom_constraints.save_as(values["-SAVE_CUSTOM_AS-"])
        if event == "-READ_CUSTOM-":
            custom_constraints = CustomConstraints()
            custom_constraints.read_constraints(values["-READ_CUSTOM-"])
            ct_update = pd.DataFrame(custom_constraints.custom_constraints)
            window["-CUSTOM_TABLE-"].Update(ct_update.values.tolist())
        if event == "-SAVE_CV_AS-":
            custom_verify.validation_summary.to_csv(values["-SAVE_CV_AS-"])

    window.close()


if __name__ == "__main__":
    main()
