import re
from pathlib import Path
from utilities import parser_utility as util


class NarberalGamma:
    cpp_code: str

    table: list = [
        ["int", "for", "cout", "cin"],
        ["<", ">", "<<", ">>", "++", "--"],
        ["{", "}", "(", ")", ";"],
        [],  # кортеж (ключ, значение)
        set(),  # set объявленных значений
    ]

    # table: dict = {
    #     "keywords": ["int", "for", "cout", "cin"],
    #     "operators": ["<", ">", "<<", ">>", "++", "--"],
    #     "delimiters": ["{", "}", "(", ")", ";"],
    #     "values": [],
    #     "declared": set()
    # }

    parsed_table: list = []

    def __init__(self, filename):
        self.read_file(filename)

    def read_file(self, filename):
        path = Path(__name__).cwd() / "input" / filename
        with open(path, "r") as file:
            lines = "".join(file.readlines()).replace("\n", " ")
            lines = re.sub("[ ]{2,}", "", lines)
            lines = re.sub("[ ]+=", "=", lines)
            lines = re.sub("=[ ]+", "=", lines)
            lines = re.sub("for\\(", "for (", lines)
            lines = re.sub("; ", ";", lines)
            self.cpp_code = lines
            print(self.cpp_code)

    def parse(self):
        i = 0
        while i < len(self.cpp_code):
            if self.cpp_code[i:i+3] == "int":
                i = self.handle_int(i) - 1
            elif self.cpp_code[i:i+3] == "for":
                i = self.handle_for(i) - 1
            elif self.cpp_code[i].isdigit():
                raise Exception(f"Ошибка в написании программы. Индекс ошибки: {i}")
            else:
                i = self.handle_another(i) - 1
            i += 1
        print(self.parsed_table)

    def handle_int(self, i):
        j = i
        while self.cpp_code[j] != ";":
            j += 1
        j += 1  # останавливается перед ;
        if not re.match("int [a-zA-Z0-9]+|int [a-zA-Z0-9]+=[0-9]+", self.cpp_code[i:j]):
            raise Exception("Непонятный int")
        self.parsed_table.append(f"1.1")
        substring = self.cpp_code[i+4:j]  # +4, потому что int 3 буквы и пробел 1
        print(substring)
        # Поиск переменной из подстроки (a1=1234 попытается найти a1)
        if "=" in substring:
            variable = substring[:util.get_position_before_item(substring, "=")]
        else:
            variable = substring[:util.get_position_before_item(substring, ";")]
        if variable in self.table[4]:
            raise Exception("Дважды объявленная переменная")
        else:
            self.table[4].add(variable)
        # Поиск значения из подстроки (a1=1234 попытается найти 1234)
        if "=" in substring:
            value = re.search("=([0-9]+)", substring)
            if value:
                print(value.group(1))
                self.table[3].append((variable, value.group(1)))
                self.parsed_table.append(f"4.{len(self.table[3])}")
            else:
                raise Exception("Не объявлена переменная")
        else:
            self.table[3].append((variable, ""))
            self.parsed_table.append(f"4.{len(self.table[3])}")
        return j

    def handle_for(self, i):
        j = i
        while self.cpp_code[j] != "}":
            j += 1
        j += 1  # останавливается перед ;
        substring = self.cpp_code[i + 4:j]  # +4, потому что int 3 буквы и пробел 1
        print(substring)
        return j

    def handle_another(self, i):
        j = i
        while self.cpp_code[j] != ";":
            j += 1
        j += 1  # останавливается перед ;
        substring = self.cpp_code[i:j]  # +4, потому что int 3 буквы и пробел 1
        print(substring)
        return j