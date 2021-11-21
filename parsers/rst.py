import re
from pathlib import Path
from utilities import my_utility as util
from utilities.graph_view import GraphView
from utilities.my_utility import *
from anytree import Node, findall, find, find_by_attr, findall_by_attr


class NarberalGamma:
    depth_for: int = 0
    prev_depth: int = 0
    number_for: int = 0
    cpp_code: str

    root_tree = Node(f"{number_for}")
    root_tree.data = {}
    root_tree_path = root_tree.path
    current_tree = root_tree
    current_tree.data = {}
    prev_tree = root_tree

    table: list = [
        ["int", "for", "cout", "cin"],
        ["<", ">", "<<", ">>", "++", "--"],
        ["{", "}", "(", ")", ";"],
        [],  # кортеж (ключ, значение)
        set(),  # set объявленных значений
        dict(),  # пробный отлов ошибок из-за видимости переменных
    ]

    graph: list = []

    parsed_table: list = []

    def __init__(self, filename):
        self.read_file(filename)

    def read_file(self, filename):
        path = Path(__name__).cwd() / "input" / get_lang_by_file(filename) / filename
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
            lines = re.sub(r"\{[ ]*", "{", lines)
            lines = re.sub(r"\}[ ]*", "}", lines)
            lines = re.sub(r"\)\{", ") {", lines)
            self.cpp_code = lines

    def parse(self, code):
        """
        @TODO перестроить под возможную рекурсию (добавить в параметры текст, который можно было бы прогонять в цикле)
        :return:
        """
        i = 0
        while i < len(code):
            if code[i:i + 3] == "int":
                i = self.handle_int(i, code) - 1
            elif code[i:i + 3] == "for" and code[i + 3] == " ":
                i = self.handle_for(i, code) - 1
            elif code[i].isdigit():
                raise Exception(f"Ошибка в написании программы. Индекс ошибки: {i}")
            else:
                i = self.handle_another(i, code) - 1
            i += 1

    def handle_int(self, i, code):
        """
        @TODO написать комментарии к коду
        @TODO добавить обработку int var1 = var2 и int var1 = 1 + 1?
        :param code:
        :param i:
        :return:
        """
        j = i
        while code[j] != ";":
            j += 1
        j += 1  # останавливается перед ;
        if not re.match("int [a-zA-Z0-9]+;|int [a-zA-Z0-9]+=[0-9]+;|int [a-zA-Z0-9]+=[a-zA-Z0-9]+;", code[i:j]):
            raise Exception("Непонятный int")
        self.parsed_table.append(f"1.1")
        substring = code[i + 4:j]  # int+пробел

        # @TODO отследить повторное объявление
        top_level_var = None
        if is_var_digit(substring[:-1]):
            top_level_var, var2 = substring.split("=")
            var2 = var2[:-1]
            self.table[3].append((top_level_var, var2))
            self.graph.append(GraphView(type="int", keywords={"variable": top_level_var, "value": var2}))
        elif is_var_var(substring[:-1]):
            top_level_var, var2 = substring.split("=")
            var2 = var2[:-1]
            self.check_context(var2)
            if not self.search_reassign_variable_in_graph(var2):
                raise Exception("Переприсваивание на empty переменную")
            self.table[3].append((top_level_var, var2))
            self.graph.append(GraphView(type="int", keywords={"variable": top_level_var, "value": var2}))
        elif is_var(substring[:-1]):
            top_level_var = substring[:-1]
            self.graph.append(GraphView(type="empty_int", keywords={"variable": top_level_var, "value": ""}))
            self.table[3].append((top_level_var, ""))
        else:
            raise Exception("Неверная инициализация переменной")

        self.parsed_table.append(f"4.{len(self.table[3])}")
        if top_level_var not in self.table[4]:
            self.table[4].add(top_level_var)
        else:
            raise Exception("Повторное объявление переменной")
        self.table[5][top_level_var] = {"depth": self.depth_for, "context": self.number_for}
        self.current_tree.data[top_level_var] = self.depth_for

        # ----------------------------------------

        # Поиск переменной из подстроки (a1=1234 попытается найти a1)
        # if "=" in substring:
        #     variable = substring[:util.get_position_before_item(substring, "=")]
        #     var1, var2 = substring.split("=")
        #     var2 = var2[:-1]  # убирает ;
        #     if not var2.isdigit():
        #         self.check_context(var2)
        # else:
        #     variable = substring[:util.get_position_before_item(substring, ";")]
        # if variable in self.table[4]:  # Тут надо чёта тоже будет делать с видимостью
        #     raise Exception("Повторно объявленная переменная")
        # else:
        #     self.table[4].add(variable)
        #     self.table[5][variable] = {"depth": self.depth_for, "context": self.number_for}
        #     self.current_tree.data[variable] = self.depth_for
        # # Поиск значения из подстроки (a1=1234 попытается найти 1234)
        # # @TODO исправить предикат, чёта придумать с ифом
        # if "=" in substring:
        #     value = re.search(r"=([0-9]+)", substring)
        #     if value:
        #         # print(value.group(1))
        #         self.table[3].append((variable, value.group(1)))
        #         self.graph.append(GraphView(type="int", keywords={"variable": variable, "value": value.group(1)}))
        #         self.parsed_table.append(f"4.{len(self.table[3])}")
        #     else:
        #         raise Exception("Не объявлена переменная")
        # else:
        #     self.table[3].append((variable, ""))
        #     self.graph.append(GraphView(type="empty_int", keywords={"variable": variable, "value": ""}))
        #     self.parsed_table.append(f"4.{len(self.table[3])}")
        return j

    def handle_for(self, i, code):
        """
        @TODO сделать эту поебень
        :param code:
        :param i:
        :return:
        """
        self.prev_depth = self.depth_for
        self.number_for += 1

        if self.number_for == 8:
            print("KEK")

        self.depth_for += 1

        self.current_tree = Node(f"{self.number_for}", parent=self.current_tree)
        self.current_tree.data = {}

        j = util.search_closing_bracket(code, i) + 1
        substring = code[i + 4:j]  # +4, потому что int 3 буквы и пробел 1
        self.parsed_table.append("1.2")
        self.parsed_table.append("3.3")
        predicate_index = util.get_position_before_item(substring, ")") + 1
        predicate = substring[1:predicate_index - 1]
        body_index = predicate_index + 1
        body = substring[body_index + 1:util.search_closing_bracket(substring, 0)]
        parsed_predicate = self.handle_cycle_predicate(predicate)
        self.graph.append(GraphView(type="for", keywords={"predicate": parsed_predicate}))
        self.graph.append(GraphView(type="for_start", keywords={}))
        self.handle_cycle_body(body)
        self.depth_for -= 1
        self.current_tree = self.current_tree.parent
        self.graph.append(GraphView(type="for_end", keywords={}))
        return j

    def handle_cycle_predicate(self, predicate) -> dict:
        """
        @TODO написать комментарии к коду, реализовать метод
        Default predicate c;c<5;c++
        :param predicate:
        :return:
        """
        step = 1
        var, pred, counter = predicate.split(";")
        if re.match("int [a-zA-Z0-9]+=[a-zA-Z0-9]+", var):
            self.handle_int(0, var + ";")
        elif re.match("[a-zA-Z0-9]+=[a-zA-Z0-9]+", var):
            self.handle_another(0, var + ";")
        else:
            self.check_context(var)
        if "<" in pred:
            # for var in range(container[0], container[1], step)
            container = pred.split("<")
        elif ">" in pred:
            # for var in range(container[0], container[1], -step)
            container = pred.split(">")
        else:
            raise Exception("Без предиката не сработает в удаве")
        var_counter = counter.split("++")

        if not str(container[0]).isdigit():
            self.check_context(container[0])
        if not str(container[1]).isdigit():
            self.check_context(container[1])

        if container[0].isdigit() and container[1].isdigit():
            if int(container[0]) != int(container[1]):
                raise Exception("Нереализумый предикат: left int, right int, not equal")

        # if var_counter[0] != container[0]:
        #     raise Exception("Инкрементируется другое значение. Бесконечный цикл.")
        return {"var": var_counter[0], "start": container[0], "end": container[1], "step": step}

    def is_increment(self, code):
        if "++" in code:
            return True
        else:
            return False

    def handle_cycle_body(self, body):
        """
        @TODO написать комментарии к коду, реализовать метод
        Default body int d=4;int y=5;
        :param body:
        :return:
        """
        self.parse(body)

    def handle_another(self, i, code):
        """
        @TODO написать комментарии к коду
        :param code:
        :param i:
        :return:
        """
        j = util.get_position_before_item(code, ";", i) + 1
        substring = code[i:j]
        if re.match("[a-zA-Z0-9]+=[0-9]+;", substring):
            lst = substring.split("=")
            variable = lst[0]
            self.check_context(variable)
            value = lst[1][:-1]
            if variable in self.table[4]:
                self.table[3].append((variable, value))
                self.graph.append(GraphView(type="reassignment", keywords={"variable": variable, "value": value}))
                self.parsed_table.append(f"4.{len(self.table[3])}")
            else:
                raise Exception("Использование переменной до инициализации")
        elif re.match("[a-zA-Z0-9]+\+\+;", substring):
            variable = substring.split("++")[0]

            self.check_context(variable)

            if variable in self.table[4]:
                self.graph.append(GraphView(type="increment", keywords={"variable": variable}))
            else:
                raise Exception("Использование переменной до инициализации")
        else:
            raise Exception("Писать без ошибок - удел слабых. "
                            "Кто-то будет писать так, как он захочет, только прогу я не скомпилю :)")
        return j

    def get_graph(self):
        return self.graph

    def get_depths(self):
        return f"depth_for: {self.depth_for}\tprev_depth: {self.prev_depth}"

    def check_context(self, variable):
        local_tree = self.current_tree
        while local_tree is not None:
            data = local_tree.data
            if variable in data:
                return True
            local_tree = local_tree.parent
        raise Exception(f"Переменная {variable} находится вне области видимости или была использована до инициализации")

    def search_reassign_variable_in_graph(self, variable):
        for item in self.graph:
            if item.type == "int" or item.type == "reassignment":
                if item.keywords["variable"] == variable:
                    if item.keywords["value"] != '':
                        return True
        return False
