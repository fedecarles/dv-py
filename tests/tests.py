"""This module has unit tests for the dataframe-validation"""

import unittest
import pandas as pd
import numpy as np
from constraints_data import ConstraintsData
from constraints import Constraints
from verifier import Verifier

# Testing data from Kaggle:
# https://www.kaggle.com/datasets/jillanisofttech/brain-stroke-dataset

constraints_data = pd.read_csv(
        r"test_data/brain_stroke.csv"
        )
validation_data = pd.read_csv(
        r"test_data/brain_stroke_bad.csv"
        )


d1 = ConstraintsData(constraints_data)
const = Constraints(d1.data).generate_constraints()
d2 = ConstraintsData(validation_data)


class TestConstraints(unittest.TestCase):
    """Test cases for DataDiscoverer"""

    data = Constraints(d1.data)

    def test_discovery(self) -> None:
        """Test data type"""
        self.assertEqual(
                self.data.get_data_type("stroke"), bool
                )
        self.assertEqual(
                self.data.is_nullable("gender"), False
                )
        self.assertEqual(
                self.data.is_unique("bmi"), False
                )
        self.assertEqual(
                self.data.max_length("avg_glucose_level"), 18
                )
        self.assertEqual(
                self.data.min_length("avg_glucose_level"), 4
                )
        self.assertIn(
                self.data.value_range("work_type").categories.all(),
                ["Private", "Self-employed", "Govt_job", "children"]
                )
        self.assertEqual(
                self.data.min_value("avg_glucose_level"),
                np.float32(55.12)
            )
        self.assertEqual(
                self.data.max_value("avg_glucose_level"),
                np.float32(271.74)
                )
        self.assertIs(
                type(self.data.generate_constraints()), dict
                )


class TestVerifier(unittest.TestCase):
    """Test cases for DataVerifier"""

    d2 = Verifier(d2.data, const)

    def test_checks(self):
        """Test null values"""
        self.assertEqual(self.d2.check_nullable(
            const["age"]["nullable"], "age"), 5)
        self.assertEqual(self.d2.check_unique(
            const["gender"]["unique"], "gender"), 0)
        self.assertEqual(self.d2.check_min_length(
            const["gender"]["min_length"], "gender"), 1)
        self.assertEqual(self.d2.check_max_length(
            const["Residence_type"]["max_length"], "Residence_type"), 2)
        self.assertEqual(self.d2.check_value_range(
            const["work_type"]["value_range"], "work_type"), 3)
        self.assertEqual(self.d2.check_max_value(
            const["bmi"]["max_value"], "bmi"), 1)
        self.assertEqual(self.d2.check_min_value(
            const["bmi"]["min_value"], "bmi"), 1)


if __name__ == '__main__':
    unittest.main()
