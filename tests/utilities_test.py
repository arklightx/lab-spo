import unittest
from utilities.my_utility import *


class TestMyUtility(unittest.TestCase):

    def test_search_closing_bracket1(self):
        text = "int a;for () {{} {} {}}int z;"
        self.assertEqual(search_closing_bracket(text, 0), 22)

    def test_search_closing_bracket2(self):
        text = "for () {{} {} {}}"
        self.assertEqual(search_closing_bracket(text, 0), 16)

    def test_get_lang_by_file_cpp(self):
        file = "main.cpp"
        self.assertEqual(get_lang_by_file(file), "cpp")

    def test_get_lang_by_file_pas(self):
        file = "main.pas"
        self.assertEqual(get_lang_by_file(file), "pascal")

    def test_get_lang_by_file_py(self):
        file = "main.py"
        self.assertEqual(get_lang_by_file(file), "python")

    def test_get_lang_by_file_exception(self):
        file = "main.wave"
        with self.assertRaises(Exception):
            get_lang_by_file(file)


if __name__ == '__main__':
    unittest.main()
