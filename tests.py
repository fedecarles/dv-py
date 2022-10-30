"""This module has unit tests for the dataframe_validation"""

import unittest
import pandas as pd
import numpy as np
from constraints import Constraints
from verifier import Verifier

# Testing data from Kaggle:
# https://www.kaggle.com/datasets/jillanisofttech/brain-stroke-dataset

d1 = pd.read_csv(r"test_data/brain_stroke.csv")
d2 = pd.read_csv(r"test_data/brain_stroke_bad.csv")
c1 = Constraints()
c1.generate_constraints(d1.data)
c1.modify_constraint("age", {"unique": True})
c1 = c1.constraints
v1 = Verifier(d2.data, c1)


class TestConstraints(unittest.TestCase):
    """Test cases for DataDiscoverer"""

    data = Constraints()

    def test_discovery(self) -> None:
        """Test data type"""
        self.assertEqual(self.data.get_data_type(d1.data, "stroke"), "bool")
        self.assertEqual(self.data.is_nullable(d1.data, "gender"), False)
        self.assertEqual(self.data.is_unique(d1.data, "bmi"), False)
        self.assertEqual(self.data.max_length(d1.data, "Residence_type"), 5)
        self.assertEqual(self.data.min_length(d1.data, "Residence_type"), 5)
        self.assertEqual(
            self.data.value_range(d1.data, "work_type"),
            {"Govt_job", "Private", "Self-employed", "children", np.NaN},
        )
        self.assertEqual(
            self.data.min_value(d1.data, "avg_glucose_level"),
            np.float32(55.12),
        )
        self.assertEqual(
            self.data.max_value(d1.data, "avg_glucose_level"),
            np.float32(271.74),
        )
        self.assertIs(type(self.data.constraints), dict)


class TestVerifier(unittest.TestCase):
    """Test cases for DataVerifier"""

    v1 = Verifier(d2.data, c1)

    def test_checks(self):
        """Test null values"""
        self.assertEqual(
            self.v1.check_nullable(c1["age"]["nullable"], "age"), 5
        )
        self.assertEqual(
            self.v1.check_unique(c1["age"]["unique"], "age"), 4876
        )
        self.assertEqual(
            self.v1.check_min_length(c1["gender"]["min_length"], "gender"), 1
        )
        self.assertEqual(
            self.v1.check_max_length(
                c1["Residence_type"]["max_length"], "Residence_type"
            ),
            2,
        )
        self.assertEqual(
            self.v1.check_value_range(
                c1["work_type"]["value_range"], "work_type"
            ),
            3,
        )
        self.assertEqual(
            self.v1.check_max_value(c1["bmi"]["max_value"], "bmi"), 1
        )
        self.assertEqual(
            self.v1.check_min_value(c1["bmi"]["min_value"], "bmi"), 1
        )


if __name__ == "__main__":
    unittest.main()
