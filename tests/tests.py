import unittest
import mock

import wmi_client_wrapper as wmi

class TestCases(unittest.TestCase):
    def test_object_creation_raises_without_username(self):
        with self.assertRaises(Exception):
            wmic = wmi.WmiClientWrapper()

    def test_object_creation_raises_without_password(self):
        with self.assertRaises(Exception):
            wmic = wmi.WmiClientWrapper(username="Administrator")

    def test_object_creation_raises_without_host(self):
        with self.assertRaises(Exception):
            wmic = wmi.WmiClientWrapper(username="Administrator", password="password")

    def test_object_creation(self):
        wmic = wmi.WmiClientWrapper(username="Administrator", password="password", host="192.168.1.173")

if __name__ == "__main__":
    unittest.main()
