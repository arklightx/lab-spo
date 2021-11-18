import re
from pathlib import Path
from utilities import parser_utility as util


class NarberalGamma:

    output_dir: str = Path(__name__).cwd() / "output" / "output.py"

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
            lines = re.sub("[ ]{2,}", " ", lines)
            lines = re.sub("[ ]+=", "=", lines)
            lines = re.sub("=[ ]+", "=", lines)
            # lines = re.sub("for\\(", "for (", lines)
            lines = re.sub("for[ ]*\\(", "for (", lines)
            lines = re.sub("; ", ";", lines)
            lines = re.sub(" ;", ";", lines)
            lines = re.sub("cout ", "cout", lines)
            lines = re.sub("<< ", "<<", lines)
            lines = re.sub("cin ", "cin", lines)
            lines = re.sub(">> ", ">>", lines)
            lines = re.sub("[ ]*<[ ]*", "<", lines)
            lines = re.sub("[ ]*>[ ]*", ">", lines)
            lines = re.sub("\{[ ]*", "{", lines)
            lines = re.sub("\}[ ]*", "}", lines)
            lines = re.sub("\)\{", ") {", lines)
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
        if not re.match("int [a-zA-Z0-9]+;|int [a-zA-Z0-9]+=[0-9]+;", self.cpp_code[i:j]):
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
        """
        @TODO сделать эту поебень
        :param i:
        :return:
        """
        j = i
        while self.cpp_code[j] != "}":
            j += 1
        j += 1  # останавливается перед ;
        substring = self.cpp_code[i + 4:j]  # +4, потому что int 3 буквы и пробел 1
        print(substring)
        self.parsed_table.append("1.2")
        self.parsed_table.append("3.3")
        predicate_index = util.get_position_before_item(substring, ")") + 1
        predicate = substring[1:predicate_index-1]
        body_index = predicate_index + 1
        body = substring[body_index + 1:util.get_position_before_item(substring, "}")]
        print(predicate)
        print(body)
        self.handle_cycle_predicate(predicate)
        self.handle_cycle_body(body)
        return j

    def handle_cycle_predicate(self, predicate):
        ...

    def handle_cycle_body(self, body):
        ...

    def handle_another(self, i):
        j = i
        while self.cpp_code[j] != ";":
            j += 1
        j += 1  # останавливается перед ;
        substring = self.cpp_code[i:j]
        print(substring)
        if not re.match("[a-zA-Z0-9]+=[0-9]+;", substring):
            raise Exception("Писать без ошибок - удел слабых. Кто-то будет писать так, как он захочет, только прогу я не скомпилю :)")
        lst = substring.split("=")
        variable = lst[0]
        value = lst[1]
        if variable in self.table[4]:
            self.table[3].append((variable, value))
            self.parsed_table.append(f"4.{len(self.table[3])}")
        else:
            raise Exception("Использование переменной до инициализации")
        return j
