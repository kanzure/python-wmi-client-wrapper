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

    def test__parse_wmic_output_merging(self):
        filepath = os.path.join(datapath, "multiple.txt")

        with open(filepath) as wmic_output_file_handler:
            # get the test data
            wmic_output = wmic_output_file_handler.read()

            # parse the data (run the function we're testing)
            result = wmi.WmiClientWrapper._parse_wmic_output(wmic_output, delimiter="%")

            # There are multiple classes listed in the data file. But they all
            # have the same number of columns. Therefore I think it's probably
            # okay to just merge all of the entries together into the same
            # list. Another possibility is to just return a list of lists,
            # instead of a list of dicts.
            self.assertTrue(isinstance(result, list))
            self.assertTrue(isinstance(result[0], dict))

            row = result[0]
            self.assertIn("Caption", row)
            self.assertIn("Description", row)

            self.assertNotIn({"AcceptPause": "CLASS: Win32_Service"}, result)

class DictionaryWalkingTestCases(unittest.TestCase):
    def test_basic_dictionary_output(self):
        incoming = {}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertEqual(incoming, output)

    def test_null_conversion(self):
        incoming = {"hello": "(null)"}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertNotEqual(incoming, output)
        self.assertIn("hello", output)
        self.assertEqual(output["hello"], None)

    def test_true_conversion(self):
        keyname = "beep"
        incoming = {keyname: "True"}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertNotEqual(incoming, output)
        self.assertIn(keyname, output)
        self.assertEqual(output[keyname], True)
        self.assertTrue(output[keyname] is True)

    def test_false_conversion(self):
        keyname = "beep"
        incoming = {keyname: "False"}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertNotEqual(incoming, output)
        self.assertIn(keyname, output)
        self.assertEqual(output[keyname], False)
        self.assertTrue(output[keyname] is False)

    def test_nested_null_conversion(self):
        keyname = "boop"
        incoming = {keyname: {keyname: "(null)"}}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertNotEqual(incoming, output)
        self.assertIn(keyname, output)
        self.assertIn(keyname, output[keyname])
        self.assertEqual(output[keyname][keyname], None)

    def test_string_length(self):
        # used to crash wth "IndexError: string index out of range"
        keyname = "boop"
        incoming = {keyname: ""}

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

    def test_lists_with_embedded_dictionaries(self):
        incoming = [{"beep": "(null)"}]

        output = wmi.WmiClientWrapper._fix_dictionary_output(incoming)

        self.assertNotEqual(incoming, output)
        self.assertIn("beep", output[0])
        self.assertEqual(output[0]["beep"], None)

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

    @mock.patch("wmi_client_wrapper.wrapper.WmiClientWrapper._parse_wmic_output")
    @mock.patch("wmi_client_wrapper.wrapper.sh.wmic")
    def test_query_calls(self, mock_sh_wmic, mock_parser):
        self.wmic.query("")

        self.assertTrue(mock_sh_wmic.called)
        self.assertTrue(mock_parser.called)

if __name__ == "__main__":
    unittest.main()
