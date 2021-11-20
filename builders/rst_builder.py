from pathlib import Path

from utilities.graph_view import GraphView
from utilities.my_utility import get_lang_by_file


class EchoOfTerror:
    graph: list[GraphView]
    file: str
    code: str

    def __init__(self, graph: list[GraphView], file: str):
        self.graph = graph
        self.file = Path(__name__).cwd() / "output" / get_lang_by_file(file) / file

    def build(self):
        with open(self.file, "w") as file:
            tab_size = 0
            for item in self.graph:
                string = "".ljust(tab_size, "\t")
                if item.type == "int":
                    string = string + f"{item.keywords['variable']} = {item.keywords['value']}"
                # elif item.type == "empty_int":
                #     ...
                elif item.type == "reassignment":
                    string = string + f"{item.keywords['variable']} = {item.keywords['value']}"
                elif item.type == "for":
                    string = string + f"for {item.keywords['predicate']['start']} in " \
                                      f"range({item.keywords['predicate']['start']}, " \
                                      f"{item.keywords['predicate']['end']}, " \
                                      f"{item.keywords['predicate']['step']}):"
                elif item.type == "for_start":
                    tab_size += 1
                    continue
                elif item.type == "for_end":
                    tab_size -= 1
                    continue
                elif item.type == "increment":
                    string = string + f"{item.keywords['variable']} += 1"
                else:
                    continue
                file.write(f"{string}\n")

    def read_file(self):
        with open(self.file, "r") as file:
            print(file.read())


