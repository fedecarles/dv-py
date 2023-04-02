"""This module has unit tests for the dataframe_validation"""

import unittest
import pandas as pd
import numpy as np
from constraints import StandardConstraints, CustomConstraints
from verifiers import StandardVerifier

# Testing data from Kaggle:
# https://www.kaggle.com/datasets/jillanisofttech/brain-stroke-dataset

d1 = pd.read_csv(r"test_data/brain_stroke.csv")
d2 = pd.read_csv(r"test_data/brain_stroke_bad.csv")
s = StandardConstraints()
s.generate_constraints(d1)
s.modify_constraint("work_type", {"nullable": False})
s.modify_constraint("age", {"unique": True})

c = CustomConstraints()
c.add_custom_constraint("rule1", "age > 80")
c.add_custom_constraint("rule2", "gender == 'Female'")
c.add_custom_constraint("rule3", "gender == 'Male'")


class TestConstraints(unittest.TestCase):
    """Test cases for StandardConstraints"""

    def test_discovery(self) -> None:
        """Test data type"""
        self.assertEqual(s.get_data_type(d1, "stroke"), "bool")
        self.assertEqual(s.is_nullable(d1, "gender"), False)
        self.assertEqual(s.is_unique(d1, "bmi"), False)
        self.assertEqual(s.max_length(d1, "Residence_type"), 5)
        self.assertEqual(s.min_length(d1, "Residence_type"), 5)
        self.assertEqual(
            s.value_range(d1, "work_type"),
            {"Govt_job", "Private", "Self-employed", "children", np.NaN},
        )
        self.assertEqual(
            s.min_value(d1, "avg_glucose_level"),
            55.12,
        )
        self.assertEqual(
            s.max_value(d1, "avg_glucose_level"),
            271.74,
        )
        self.assertIs(type(s.constraints), dict)


class TestVerifier(unittest.TestCase):
    """Test cases for DataVerifier"""

    v1 = StandardVerifier(d1, s.constraints)

    def test_checks(self):
        """Test null values"""
        self.assertEqual(
            self.v1.check_nullable(s.constraints["age"]["nullable"], "age"), 0
        )
        self.assertEqual(
            self.v1.check_unique(s.constraints["age"]["unique"], "age"), 4877
        )
        self.assertEqual(
            self.v1.check_min_length(
                s.constraints["gender"]["min_length"], "gender"
            ),
            0,
        )
        self.assertEqual(
            self.v1.check_max_length(
                s.constraints["Residence_type"]["max_length"], "Residence_type"
            ),
            0,
        )
        self.assertEqual(
            self.v1.check_max_value(s.constraints["bmi"]["max_value"], "bmi"),
            0,
        )
        self.assertEqual(
            self.v1.check_min_value(s.constraints["bmi"]["min_value"], "bmi"),
            0,
        )


if __name__ == "__main__":
    unittest.main()
