""" GUI Layouts"""

import PySimpleGUI as sg

sg.theme("DarkBlue2")
sg.set_options(font=("Arial", 12))

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
CUSTOM_HEADINGS = ["name", "rule", "count"]
DTYPES = ["category", "bool", "float", "int", "str", "datetime64[ns]"]

standard_constraint_properties = [
    [sg.T("attribute: ", key="attribute")],
    [
        sg.T("data_type: ", size=(11, 1)),
        sg.Combo(DTYPES, size=(10, 1), key="data_type"),
    ],
    [
        sg.T("nullable: ", size=(11, 1)),
        sg.Combo([True, False], size=(10, 1), key="nullable"),
    ],
    [
        sg.T("unique: ", size=(11, 1)),
        sg.Combo([True, False], size=(10, 1), key="unique"),
    ],
    [sg.T("min_length: ", size=(11, 1)), sg.I(size=(11, 1), key="min_length")],
    [sg.T("max_length: ", size=(11, 1)), sg.I(size=(11, 1), key="max_length")],
    [
        sg.T("value_range: ", size=(11, 1)),
        sg.ML(size=(10, 10), key="value_range"),
    ],
    [sg.T("min_value: ", size=(11, 1)), sg.I(size=(11, 1), key="min_value")],
    [sg.T("max_value: ", size=(11, 1)), sg.I(size=(11, 1), key="max_value")],
    [sg.T("min_date: ", size=(11, 1)), sg.I(size=(11, 1), key="min_date")],
    [sg.T("max_date: ", size=(11, 1)), sg.I(size=(11, 1), key="max_date")],
    [sg.P(), sg.B("Update")],
]

custom_constraint_properties = [
    [sg.T("name: ", size=(11, 1)), sg.I(size=(20, 1), key="-NAME-")],
    [sg.T("query: ", size=(11, 1)), sg.ML(size=(50, 10), key="-QUERY-")],
    [sg.B("Create"), sg.P(), sg.B("Delete")],
]

standard_constraints_prop_frame = [
    [
        sg.Frame(
            "Standard Constraint Properties", standard_constraint_properties
        )
    ]
]
custom_constraints_prop_frame = [
    [sg.Frame("Custom Constraint Properties", custom_constraint_properties)]
]

standard_layout = [
    [
        sg.B("Generate Constraints"),
        sg.B("Recast dtypes"),
        sg.I(visible=False, enable_events=True, key="-SAVE_C_AS-"),
        sg.FileSaveAs("Save Constraints"),
        sg.I(visible=False, enable_events=True, key="-READ_C-"),
        sg.FileBrowse("Load Constraints"),
    ],
    [
        sg.Table(
            values=[],
            headings=STANDARD_HEADINGS,
            auto_size_columns=False,
            enable_events=True,
            key="-STANDARD_TABLE-",
            expand_x=True,
            num_rows=20,
        )
    ],
    [
        sg.B("Validate Data"),
        sg.B("Enforce dtypes", button_color="white on green", key="-DTYPES-"),
        sg.I(visible=False, enable_events=True, key="-SAVE_V_AS-"),
        sg.FileSaveAs("Save Summary", file_types=(("CSV Files", "*.csv*"),)),
    ],
    [
        sg.Table(
            values=[],
            headings=STANDARD_HEADINGS,
            auto_size_columns=False,
            enable_events=True,
            key="-V_TABLE-",
            expand_x=True,
            num_rows=20,
        )
    ],
    [
        sg.T("Progress: "),
        sg.ProgressBar(
            max_value=100, orientation="h", size=(20, 20), key="-PROG-"
        ),
    ],
]

custom_layout = [
    [
        sg.I(visible=False, enable_events=True, key="-SAVE_CUSTOM_AS-"),
        sg.FileSaveAs("Save Constraints"),
        sg.I(visible=False, enable_events=True, key="-READ_CUSTOM-"),
        sg.FileBrowse("Load Constraints"),
    ],
    [
        sg.Table(
            values=[],
            headings=["name", "query"],
            auto_size_columns=False,
            enable_events=True,
            key="-CUSTOM_TABLE-",
            expand_x=True,
            num_rows=20,
            def_col_width=40
        )
    ],
    [
        sg.B("Validate Custom"),
        sg.I(visible=False, enable_events=True, key="-SAVE_CV_AS-"),
        sg.FileSaveAs("Save Summary", file_types=(("CSV Files", "*.csv*"),)),
    ],
    [
        sg.Table(
            values=[],
            headings=CUSTOM_HEADINGS,
            auto_size_columns=False,
            enable_events=True,
            key="-CV_TABLE-",
            expand_x=True,
            num_rows=20,
        )
    ],
    [
        sg.T("Progress: "),
        sg.ProgressBar(
            max_value=100, orientation="h", size=(20, 20), key="-CV_PROG-"
        ),
    ],
]

standard_layout_columns = [
    [sg.Column(standard_layout), sg.Column(standard_constraints_prop_frame)]
]

custom_layout_columns = [
    [sg.Column(custom_layout), sg.Column(custom_constraints_prop_frame)]
]

tabgrp = [
    [
        sg.T("Data File: "),
        sg.I(enable_events=True, key="-IN-"),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv*"),)),
    ],
    [
        sg.TabGroup(
            [
                [sg.Tab("Standard Constraints", standard_layout_columns)],
                [sg.Tab("Custom Constraints", custom_layout_columns)],
            ]
        )
    ],
    [sg.Exit()],
]
