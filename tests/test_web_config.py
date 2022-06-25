"""
This file tests the construction of the WebConfig class and how it manages config data.
"""
import os
import sys
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

from ybconfig.web_config import WebConfig
from ybconfig.singleton import Singleton


class TestWebConfig(TestCase):

    @patch("ybconfig.web_config.WebConfig.load")
    def setUp(self, mock_load) -> None:
        self.test = WebConfig()
        self.directory_path: str = str(Path(__file__).resolve()).replace("test_web_config.py", "")
        self.config_path: str = self.directory_path + "meta_data/some_config.yml"
        self.sys_args = sys.argv

    def tearDown(self) -> None:
        Singleton._instances = {}
        os.environ["ENVIRONMENT_CONFIG"] = ""
        sys.argv = [sys.argv[0]]

    def test_file_path(self) -> None:
        sys.argv.append(self.config_path)
        self.assertEqual(self.config_path, self.test.file_path)

    def test_from_file(self):
        self.assertEqual(True, self.test.from_file)

        os.environ["ENVIRONMENT_CONFIG"] = "false"
        self.assertEqual(True, self.test.from_file)

        os.environ["ENVIRONMENT_CONFIG"] = "true"
        self.assertEqual(False, self.test.from_file)

    def test__load_from_file(self):
        sys.argv.append(self.config_path)
        self.test._load_from_file()

        self.assertEqual(EXPECTED_CONFIG, self.test)

    def test_load(self):
        Singleton._instances = {}
        os.environ["ENVIRONMENT_CONFIG"] = "true"
        test = WebConfig()
        self.assertEqual({}, test)

        Singleton._instances = {}
        sys.argv.append(self.config_path)
        os.environ["ENVIRONMENT_CONFIG"] = "false"
        test = WebConfig()
        self.assertEqual(EXPECTED_CONFIG, test)

    def test_get(self):
        sys.argv.append(self.config_path)
        self.test.load()
        os.environ["ONE"] = "something"

        self.assertEqual(1, self.test.get("ONE"))
        self.assertEqual(1, self.test.get("ONE", file=True))

        self.assertEqual("something", self.test.get("ONE", environ=True))

        self.assertEqual(None, self.test.get("ONES"))
        self.assertEqual(None, self.test.get("ONES", environ=True))

        with self.assertRaises(KeyError) as key_error:
            self.test.get("ONES", strict=True)
        self.assertEqual("'ONES not found'", str(key_error.exception))

        with self.assertRaises(KeyError) as key_error:
            self.test.get("ONES", strict=True, environ=True)
        self.assertEqual("'ONES not found'", str(key_error.exception))

        with self.assertRaises(KeyError) as key_error:
            self.test.get("ONE", environ=True, file=True)
        self.assertEqual("'file and environ both cannot be True'", str(key_error.exception))

    def test_clean_memory(self):
        sys.argv.append(self.config_path)
        memory_id = id(self.test)
        new_test = WebConfig()

        self.assertEqual(memory_id, id(new_test))
        self.assertEqual({}, self.test)
        self.assertEqual({}, new_test)

        new_test.load()

        self.assertEqual(EXPECTED_CONFIG, self.test)
        self.assertEqual(EXPECTED_CONFIG, new_test)

        new_test.clean_memory()
        os.environ["ENVIRONMENT_CONFIG"] = "true"
        another_new_test = WebConfig()

        self.assertEqual(memory_id, id(new_test))
        self.assertNotEqual(id(new_test), id(another_new_test))

        self.assertEqual(EXPECTED_CONFIG, self.test)
        self.assertEqual(EXPECTED_CONFIG, new_test)
        self.assertEqual({}, another_new_test)


EXPECTED_CONFIG = {
    'ONE': 1,
    'TWO': 'two',
    'THREE': [1, 2, 3],
    'FOUR': {
        'ONE': 1,
        'TWO': 'two',
        'THREE': [1, 2, 3]
    }
}


if __name__ == '__main__':
    main()
