import re
from pathlib import Path
from utilities import my_utility as util
from utilities.graph_view import GraphView
from utilities.my_utility import get_lang_by_file
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
            lines = re.sub("\{[ ]*", "{", lines)
            lines = re.sub("\}[ ]*", "}", lines)
            lines = re.sub("\)\{", ") {", lines)
            self.cpp_code = lines

    def parse(self, code):
        """
        @TODO перестроить под возможную рекурсию (добавить в параметры текст, который можно было бы прогонять в цикле)
        :return:
        """
        i = 0
        while i < len(code):
            if self.depth_for == 0:
                self.prev_depth = 0
                self.current_tree = self.root_tree
            # else:
            #     diff = self.depth_for - self.prev_depth
            #     for a in range(diff):
            #         self.current_tree = self.current_tree.parent
            if code[i:i + 3] == "int":
                i = self.handle_int(i, code) - 1
            elif code[i:i + 3] == "for":
                i = self.handle_for(i, code) - 1
            elif code[i].isdigit():
                raise Exception(f"Ошибка в написании программы. Индекс ошибки: {i}")
            else:
                i = self.handle_another(i, code) - 1
            i += 1
        # self.check_tree()

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
        if not re.match("int [a-zA-Z0-9]+;|int [a-zA-Z0-9]+=[0-9]+;", code[i:j]):
            raise Exception("Непонятный int")
        self.parsed_table.append(f"1.1")
        substring = code[i + 4:j]  # int+пробел
        # Поиск переменной из подстроки (a1=1234 попытается найти a1)
        if "=" in substring:
            variable = substring[:util.get_position_before_item(substring, "=")]
        else:
            variable = substring[:util.get_position_before_item(substring, ";")]
        if variable in self.table[4]:  # Тут надо чёта тоже будет делать с видимостью
            raise Exception("Повторно объявленная переменная")
        else:
            self.table[4].add(variable)
            self.table[5][variable] = {"depth": self.depth_for, "context": self.number_for}
            self.current_tree.data[variable] = self.depth_for
        # Поиск значения из подстроки (a1=1234 попытается найти 1234)
        if "=" in substring:
            value = re.search("=([0-9]+)", substring)
            if value:
                # print(value.group(1))
                self.table[3].append((variable, value.group(1)))
                self.graph.append(GraphView(type="int", keywords={"variable": variable, "value": value.group(1)}))
                self.parsed_table.append(f"4.{len(self.table[3])}")
            else:
                raise Exception("Не объявлена переменная")
        else:
            self.table[3].append((variable, ""))
            self.graph.append(GraphView(type="empty_int", keywords={"variable": variable, "value": ""}))
            self.parsed_table.append(f"4.{len(self.table[3])}")
        return j

    def handle_for(self, i, code):
        """
        @TODO сделать эту поебень
        :param code:
        :param i:
        :return:
        """
        self.number_for += 1
        self.depth_for += 1
        self.check_tree()
        self.prev_depth = self.depth_for
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
        # self.prev_depth += 1
        # self.prev_depth = self.depth_for + 1
        # self.current_tree = self.current_tree.parent
        self.graph.append(GraphView(type="for_end", keywords={}))
        # self.prev_depth = self.depth_for
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
            self.handle_int(0, var+";")
        elif re.match("[a-zA-Z0-9]+=[a-zA-Z0-9]+", var):
            self.handle_another(0, var+";")
        else:
            ...
        # self.check_tree()
        # if var not in self.table[4]:
        #     raise Exception("Переменная не объявлена, но юзается в for")
        if "<" in pred:
            # for var in range(container[0], container[1], step)
            container = pred.split("<")
        elif ">" in pred:
            # for var in range(container[0], container[1], -step)
            container = pred.split(">")
        else:
            raise Exception("Без предиката не сработает в удаве")
        var_counter = counter.split("++")
        if var_counter[0] != container[0]:
            raise Exception("Инкрементируется другое значение. Бесконечный цикл.")
        return {"start": container[0], "end": container[1], "step": step}

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
        try:
            self.parse(body)
            # self.current_tree = self.current_tree.parent
        except:
            print(self.current_tree)
            print(self.depth_for)
            print(self.prev_depth)

    def handle_another(self, i, code):
        """
        @TODO написать комментарии к коду
        :param code:
        :param i:
        :return:
        """
        j = util.get_position_before_item(code, ";", i) + 1
        substring = code[i:j]
        # print(substring)
        if re.match("[a-zA-Z0-9]+=[0-9]+;", substring):
            lst = substring.split("=")
            variable = lst[0]
            if self.table[5][variable]["depth"] > self.depth_for:
                raise Exception(f"Нарушена область видимости. "
                                f"Переменная {variable} объявлена на уровне {self.table[5][variable]['depth']}, "
                                f"однако идёт попытка переопределить на уровне {self.depth_for}")
            elif self.table[5][variable]["context"] != self.number_for:
                ...
            value = lst[1][:-1]
            if variable in self.table[4]:
                self.table[3].append((variable, value))
                self.graph.append(GraphView(type="reassignment", keywords={"variable": variable, "value": value}))
                self.parsed_table.append(f"4.{len(self.table[3])}")
            else:
                raise Exception("Использование переменной до инициализации")
        elif re.match("[a-zA-Z0-9]+\+\+;", substring):
            variable = substring.split("++")[0]
            if self.table[5][variable]["depth"] > self.depth_for:
                raise Exception(f"Нарушена область видимости. "
                                f"Переменная {variable} объявлена на уровне {self.table[5][variable]['depth']}, "
                                f"однако идёт попытка переопределить на уровне {self.depth_for}")
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

    def check_tree(self):
        if self.prev_depth < self.depth_for:
            node = Node(self.number_for, parent=self.current_tree)
            self.current_tree = node
        elif self.prev_depth == self.depth_for:
            node = Node(self.number_for, parent=self.current_tree.parent)
            self.current_tree = node
        elif self.prev_depth > self.depth_for:
            diff = self.prev_depth - self.depth_for
            # parent_node = self.current_tree.parent
            for i in range(diff+1):
                self.current_tree = self.current_tree.parent
            node = Node(self.number_for, parent=self.current_tree)
            self.current_tree = node
            # print(f"[\n\tdiff: {diff}\n\tprev: {self.prev_depth}\n\t"
            #       f"depth: {self.depth_for}\n\tnode: {self.current_tree}\n\t"
            #       f"root_tree: {self.root_tree.descendants}\n]")
        else:
            self.current_tree = self.root_tree
        # try:
        #     self.current_tree.__getattribute__("data")
        # except:
        self.current_tree.data = {}

    def get_depths(self):
        return f"depth_for: {self.depth_for}\tprev_depth: {self.prev_depth}"
