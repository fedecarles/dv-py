<!-- [START BADGES] -->
[![Pylint](https://github.com/fedecarles/dataframe-validation/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/fedecarles/dataframe-validation/actions/workflows/pylint.yml)
[![Tests](https://github.com/fedecarles/dataframe-validation/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/fedecarles/dataframe-validation/actions/workflows/tests.yml)
<!-- [END BADGES] -->

# DataFrame-Validation

## What it does
dataframe-validation is a simplified tool to validate a pandas DataFrame 
based on pre-define rules. The rules include:

* **Null check**: Checks for null values in a DataFrame column.
* **Unique check**: Checks if a column has duplicate values.
* **Max Length**: Checks if a string value in a DataFrame column exceeds the maximum number of characters.
* **Min Length**: Checks if a string value in a DataFrame column exceeds the minimum number of characters.
* **Value Range**: Checks if a DataFrame column has values outside the expected list of values.
* **Max Value**: Checks if a value in a DataFrame column exceed the expected max value.
* **Min Value**: Checks if a value in a DataFrame column exceed the expected min value.

## To-do

* [ ] Add **Load Constraints** functionality.
* [ ] Add **Data Profile** section.

