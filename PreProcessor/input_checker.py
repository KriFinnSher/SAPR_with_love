from tkinter import messagebox
from collections import Counter


def input_is_correct(user_input):
    correct = True
    for bar in user_input["bars"]:
        for val in bar:
            if bar[val] == '':
                messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые поля в окне стержней")
                correct = False
                return correct

    for node in user_input["nodes"][1:]:
        if node == '' or float(node) == 0:
            messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые (нулевые) поля в окне узлов")
            correct = False
            return correct

    for conc_load in user_input["conc_loads"]:
        for val in conc_load:
            if conc_load[val] == '' or conc_load[val] == '-':
                messagebox.showwarning("Ошибка ввода данных",
                                       "Присутствуют пустые поля в окне сосредоточенных нагрузок")
                correct = False
                return correct

    for dist_load in user_input["dist_loads"]:
        for val in dist_load:
            if dist_load[val] == '' or dist_load[val] == '-':
                messagebox.showwarning("Ошибка ввода данных",
                                       "Присутствуют пустые поля в окне распределенных нагрузок")
                correct = False
                return correct

    if len(user_input["nodes"]) < 2:
        messagebox.showwarning("Ошибка ввода данных",
                               "В схеме должно присутствовать минимум два узла")
        correct = False
        return correct

    if not correct:
        return False

    created_nodes = set(range(1, len(user_input["nodes"]) + 1))
    created_bars = set(range(1, len(user_input["nodes"])))
    used_nodes = set()

    for bar in user_input["bars"]:
        if int(bar["first_node"]) not in created_nodes or int(bar["second_node"]) not in created_nodes:
            messagebox.showwarning("Ошибка ввода данных",
                                   "В окне стержней используются неуказанные узлы")
            correct = False
            return correct
        used_nodes.add(int(bar["first_node"]))
        used_nodes.add(int(bar["second_node"]))

        if abs(int(bar["first_node"]) - int(bar["second_node"])) != 1:
            messagebox.showwarning("Ошибка ввода данных",
                                   "Каждый стержень должен находиться между соседних узлов")
            correct = False
            return correct

    loads_num = 0
    loads_nodes = []
    for conc_load in user_input["conc_loads"]:
        loads_nodes.append(int(conc_load["node_num"]))
        if int(conc_load["node_num"]) not in created_nodes:
            messagebox.showwarning("Ошибка ввода данных",
                                   "В окне сосредоточенных нагрузок используются неуказанные узлы")
            correct = False
            return correct
        if float(conc_load["conc_load"]) != 0:
            loads_num += 1

    if max(Counter(loads_nodes).values()) > 1:
        messagebox.showwarning("Ошибка ввода данных",
                               "В каждом узле действует не более одной сосредоточенной нагрузки")
        correct = False
        return correct

    loads_bars = []
    for dist_load in user_input["dist_loads"]:
        loads_bars.append(int(dist_load["bar_num"]))
        if int(dist_load["bar_num"]) not in created_bars:
            messagebox.showwarning("Ошибка ввода данных",
                                   "В окне распределенных нагрузок используются неуказанные стержни")
            correct = False
            return correct
        if float(dist_load["dist_load"]) != 0:
            loads_num += 1

    if max(Counter(loads_bars).values()) > 1:
        messagebox.showwarning("Ошибка ввода данных",
                               "В каждом стержне действует не более одной распределенной нагрузки")
        correct = False
        return correct

    if loads_num == 0:
        messagebox.showwarning("Ошибка ввода данных",
                               "В схеме должна быть хотя бы одна ненулевая нагрузка")
        correct = False
        return correct

    if len(created_nodes) > len(used_nodes):
        messagebox.showwarning("Ошибка ввода данных",
                               "В схеме присутствуют неиспользованные узлы")
        correct = False
        return correct

    for bar in user_input["bars"]:
        if float(bar["a"]) == 0:
            messagebox.showwarning("Ошибка ввода данных", "Присутствуют пустые (нулевые) поля в окне стержней")
            correct = False
            return correct

    return correct