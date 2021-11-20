from builders.rst_builder import EchoOfTerror
from parsers.rst import NarberalGamma
from pprint import pprint
from utilities.my_utility import search_closing_bracket
import unittest
from tests import utilities_test

if __name__ == '__main__':
    # unittest.main(utilities_test)
    nabe = NarberalGamma("main.cpp")
    nabe.parse(nabe.cpp_code)
    graph = nabe.get_graph()
    pprint(graph)
    eot = EchoOfTerror(graph, "output.py")
    eot.build()
    eot.read_file()
