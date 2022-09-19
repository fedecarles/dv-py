from validators import DataDiscoverer, DataVerifier
import datetime as datetime
import pandas as pd
import unittest

data1 = pd.read_csv(r"data.csv")
data1["Importe"] = data1["Importe"].astype(float)
data2 = pd.read_csv(r"data2.csv")
data2["Importe"] = data2["Importe"].astype(float)

r1 = DataDiscoverer(data1)
const = r1.generate_constraints()


class TestDataDiscoverer(unittest.TestCase):
    data = DataDiscoverer(data1)

    def test_data_type(self) -> None:
        self.assertEqual(self.data.get_data_type("Importe"), 'float64')
        self.assertEqual(self.data.get_data_type("Establecimiento"), 'object')
        self.assertEqual(self.data.get_data_type("Cuota"), 'object')


class TestDataVerifier(unittest.TestCase):
    d2 = DataVerifier(data2, const)

    def test_nullable(self):
        result = self.d2.check_nullable(const["Establecimiento"]["nullable"], "Establecimiento")
        self.assertEqual(result, 2)

    def test_unique(self):
        result = self.d2.check_unique(const["Establecimiento"]["unique"], "Establecimiento")
        self.assertEqual(result, 1)

    

if '__name__' == '__main__':
    unittest.main()
