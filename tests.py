"""This module has unit tests for the dataframe-validation"""

import unittest
import pandas as pd
from validators import DataDiscoverer, DataVerifier

data1 = pd.read_csv(r"test_data/data.csv")
data1["Importe"] = data1["Importe"].astype(float)
data2 = pd.read_csv(r"test_data/data2.csv")
data2["Importe"] = data2["Importe"].astype(float)

r1 = DataDiscoverer(data1)
const = r1.generate_constraints()
print(const)


class TestDataDiscoverer(unittest.TestCase):
    """Test cases for DataDiscoverer"""

    data = DataDiscoverer(data1)

    def test_discovery(self) -> None:
        """Test data type"""
        self.assertEqual(self.data.get_data_type("Importe"), 'float64')
        self.assertEqual(self.data.is_nullable("Establecimiento"), False)
        self.assertEqual(self.data.is_unique("Establecimiento"), True)
        self.assertEqual(self.data.max_length("Establecimiento"), 27)
        self.assertEqual(self.data.min_length("Establecimiento"), 7)
        self.assertIn(self.data.value_range("Cuota").all(), ['/', '9/12'])
        self.assertEqual(self.data.min_value("Importe"), -752.11)
        self.assertEqual(self.data.max_value("Importe"), 5583.25)


class TestDataVerifier(unittest.TestCase):
    """Test cases for DataVerifier"""

    d2 = DataVerifier(data2, const)

    def test_checks(self):
        """Test null values"""
        self.assertEqual(self.d2.check_nullable(
            const["Establecimiento"]["nullable"], "Establecimiento"), 2)
        self.assertEqual(self.d2.check_unique(
            const["Establecimiento"]["unique"], "Establecimiento"), 1)
        self.assertEqual(self.d2.check_max_length(
            const["Establecimiento"]["max_length"], "Establecimiento"), 0)
        self.assertEqual(self.d2.check_max_length(
            const["Establecimiento"]["max_length"], "Establecimiento"), 0)
        self.assertEqual(self.d2.check_value_range(
            const["Establecimiento"]["value_range"], "Establecimiento"), 3)
        self.assertEqual(self.d2.check_max_value(
            const["Importe"]["max_value"], "Importe"), 1)
        self.assertEqual(self.d2.check_min_value(
            const["Importe"]["min_value"], "Importe"), 0)


if __name__ == '__main__':
    unittest.main()
