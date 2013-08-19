import unittest
import mock

import wmi_client_wrapper as wmi

import os

datapath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/")

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

    def test_delimiter_in_setup(self):
        expected_delimiter = "FOOBAR"

        wmic = wmi.WmiClientWrapper(
            username="Administrator",
            password="password",
            host="192.168.1.173",
            delimiter=expected_delimiter,
        )

        output = " ".join(wmic._setup_params())

        self.assertIn(expected_delimiter, output)

    def test__parse_wmic_output(self):
        filepath = os.path.join(datapath, "group.txt")

        with open(filepath) as wmic_output_file_handler:
            # get the test data
            wmic_output = wmic_output_file_handler.read()

            # parse the data (run the function we're testing)
            result = wmi.WmiClientWrapper._parse_wmic_output(wmic_output, delimiter="|")

            # true statements that should be true
            self.assertTrue(isinstance(result, list))
            self.assertTrue(isinstance(result[0], dict))

            # expected keys are expected
            row = result[0]
            self.assertIn("Caption", row)
            self.assertIn("Description", row)
            self.assertIn("Domain", row)

class MoreTestCases(unittest.TestCase):
    def setUp(self):
        self.wmic = wmi.WmiClientWrapper(
            username="boop",
            password="beep",
            host="127.0.0.2",
        )

    def tearDown(self):
        del self.wmic

    def test__make_credential_args(self):
        args = self.wmic._make_credential_args()

if __name__ == "__main__":
    unittest.main()
