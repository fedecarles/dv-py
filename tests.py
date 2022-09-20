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


class TestDataDiscoverer(unittest.TestCase):
    """Test cases for DataDiscoverer"""

    data = DataDiscoverer(data1)

    def test_data_type(self) -> None:
        """Test data type"""
        self.assertEqual(self.data.get_data_type("Importe"), 'float64')
        self.assertEqual(self.data.get_data_type("Establecimiento"), 'object')
        self.assertEqual(self.data.get_data_type("Cuota"), 'object')


class TestDataVerifier(unittest.TestCase):
    """Test cases for DataVerifier"""

    d2 = DataVerifier(data2, const)

    def test_nullable(self):
        """Test null values"""
        result = self.d2.check_nullable(
                const["Establecimiento"]["nullable"],
                "Establecimiento"
                )
        self.assertEqual(result, 2)

    def test_unique(self):
        """Test unique values"""
        result = self.d2.check_unique(
                const["Establecimiento"]["unique"],
                "Establecimiento"
                )
        self.assertEqual(result, 1)

    def test_max_length(self):
        """Test max length"""
        result = self.d2.check_max_length(
                const["Establecimiento"]["max_length"],
                "Establecimiento"
                )
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
