from builders.rst_builder import EchoOfTerror
from parsers.rst import NarberalGamma
from pprint import pprint
from utilities.my_utility import search_closing_bracket
import unittest
from tests import utilities_test
from anytree import RenderTree, AsciiStyle, ContStyle

if __name__ == '__main__':
    # unittest.main(utilities_test)
    nabe = NarberalGamma("main.cpp")
    nabe.parse(nabe.cpp_code)
    graph = nabe.get_graph()
    print(nabe.get_depths())
    # pprint(graph)
    eot = EchoOfTerror(graph, "output.py")
    eot.build()
    # eot.read_file()
    # pprint(nabe.table[5])
    # pprint(nabe.root_tree)
    print(RenderTree(nabe.root_tree, style=AsciiStyle()))
