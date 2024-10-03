import tkinter as tk
from tkinter import filedialog
import validators
from collections import defaultdict
import json
import drawing


class SaprApp:

    def __init__(self, root):
        self.root = root
        self.root.title("SAPR with love")
        root.option_add('*tearOff', 0)

        self.root.geometry("1140x570")
        self.root.resizable(False, False)

        self.user_input = defaultdict(list)
        self.last_files = []

        self.node_check = (self.root.register(validators.rational_positive_number), '%P')
        self.bar_node_check = (self.root.register(validators.natural_positive_number), '%P')
        self.bar_a_check = (self.root.register(validators.rational_positive_number), '%P')
        self.bar_e_check = (self.root.register(validators.rational_positive_number), '%P')
        self.bar_max_load_check = (self.root.register(validators.rational_positive_number), '%P')
        self.loads_check = (self.root.register(validators.rational_number), '%P')

        self.nodes_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление узлов")
        self.bars_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление стержней")
        self.loads_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление нагрузок")
        self.preview_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Полученная схема")
        self.postprocess_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Данные постпроцессора")

        self.nodes_frame.grid(row=0, column=0, padx=5, pady=10, sticky="n")
        self.bars_frame.grid(row=0, column=1, padx=5, pady=10, sticky="n")
        self.loads_frame.grid(row=0, column=2, padx=5, pady=10, sticky="n")
        self.preview_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.postprocess_frame.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")

        self.initialize_nodes_section()
        self.initialize_bars_section()
        self.initialize_loads_section()
        self.initialize_preview_section()
        self.initialize_postprocess_section()
        self.initialize_menu_section()

    def refresh(self):
        self.get_node_entries()
        self.get_bar_entries()
        self.get_conc_load_entries()
        self.get_dist_load_entries()

    def show_scheme(self):
        self.refresh()
        lengths = [float(val) for val in self.user_input["nodes"][1:]]
        heights = [0] * len(self.bar_entries)
        nodes = [0] * len(self.node_entries)
        for i in range(1, len(self.node_entries)):
            nodes[i] = float(self.user_input["nodes"][i]) + nodes[i-1]
        conc_loads = []
        for conc_load in self.user_input["conc_loads"]:
            conc_loads.append((conc_load["node_num"], float(conc_load["conc_load"]) > 0))
        for bar in self.user_input["bars"]:
            heights[int(bar["second_node"]) - 2] = float(bar["a"])
        drawing.display_scheme(self.preview_canvas, lengths, heights, nodes, conc_loads, dist_loads=None)

    def close(self):
        self.root.destroy()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Открытие файла"
        )

        if file_path:
            self.last_files.append(file_path)
            self.update_last_files()
            with open(file_path, 'r') as file:
                data = json.load(file)

            self.reset_input_for_file()
            self.user_input = data

            self.fill_nodes()
            self.fill_bars()
            self.fill_conc_load()
            self.fill_dist_load()

    def save_file(self):
        self.refresh()

        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранение файла"
        )

        if file_path:
            data = self.user_input
            with open(file_path, 'w') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Файл сохранён: {file_path}")

    def initialize_menu_section(self):
        self.menubar = tk.Menu(self.root)
        self.root["menu"] = self.menubar

        self.menu_file = tk.Menu(self.menubar, tearoff=0)
        self.menu_faq = tk.Menu(self.menubar, tearoff=0)
        self.menu_last_files = tk.Menu(self.menu_file, tearoff=0)

        self.menubar.add_cascade(menu=self.menu_file, label="Файл")
        self.menubar.add_cascade(menu=self.menu_faq, label="Справка")
        self.menu_file.add_cascade(menu=self.menu_last_files, label="Последние файлы")

        self.menu_file.add_command(label="Открыть", command=self.open_file)
        self.menu_file.add_command(label="Сохранить", command=self.save_file)
        self.menu_file.add_command(label="Сбросить ввод", command=self.reset_input)
        self.menu_file.add_command(label="Выход", command=self.close)

        self.update_last_files()

    def update_last_files(self):
        self.menu_last_files.delete(0, tk.END)
        for file in self.last_files[-5:]:
            self.menu_last_files.add_command(label=file, command=lambda f=file: self.load_last_file(f))

    def load_last_file(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

            self.reset_input_for_file()
            self.user_input = data

            self.fill_nodes()
            self.fill_bars()
            self.fill_conc_load()
            self.fill_dist_load()

    def reset_input_for_file(self):
        self.reset_node_entries()
        self.reset_bar_entries()
        self.reset_conc_load_entries()
        self.reset_dist_load_entries()

    def reset_input(self):
        self.reset_node_entries()
        self.reset_bar_entries()
        self.reset_conc_load_entries()
        self.reset_dist_load_entries()

        self.create_bar_row()
        self.create_conc_load_row()
        self.create_dist_load_row()

    def initialize_nodes_section(self):
        canvas = tk.Canvas(self.nodes_frame, width=140, height=150)
        canvas.grid(row=0, column=0, columnspan=4, sticky='nsew')

        scrollbar = tk.Scrollbar(self.nodes_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=4, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        tk.Label(self.scrollable_frame, text="S, м").grid(row=0, column=2, sticky='w')

        self.node_entries = []
        self.create_node_row()

    def create_node_row(self):
        row_index = len(self.node_entries) + 1

        frame = tk.Frame(self.scrollable_frame)
        frame.grid(row=row_index, column=0, columnspan=4, pady=2, sticky="ew")

        node_label = tk.Label(frame, text=f"Узел {row_index}:")
        node_label.grid(row=0, column=0, padx=5, sticky="w")

        node_entry = tk.Entry(frame, width=3)
        node_entry.insert(0, '0')
        node_entry.config(state='readonly')
        node_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_node_row(frame), width=2)
        add_button.grid(row=0, column=2)

        remove_button = tk.Button(frame, text="-", width=2)
        remove_button.grid(row=0, column=3)

        self.node_entries.append((frame, node_label))
        self.refresh_node_grid()

    def add_node_row(self, row_frame):
        index = self.get_node_row_index(row_frame)
        self.create_node_row_at_index(index + 1)

    def create_node_row_at_index(self, index, node_val=None):
        frame = tk.Frame(self.scrollable_frame)
        frame.grid(row=index + 1, column=0, columnspan=4, pady=2, sticky="ew")

        node_label = tk.Label(frame, text=f"Узел {index + 1}:")
        node_label.grid(row=0, column=0, padx=5, sticky="w")

        node_entry = tk.Entry(frame, width=3, validate='all', validatecommand=self.node_check)
        node_entry.grid(row=0, column=1, padx=5)

        if node_val is not None:
            node_entry.insert(0, node_val)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_node_row(frame), width=2)
        add_button.grid(row=0, column=2)

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_node_row(frame), width=2)
        remove_button.grid(row=0, column=3)

        self.node_entries.insert(index, (frame, node_label))
        self.refresh_node_grid()

    def fill_nodes(self):
        for idx, node in enumerate(self.user_input["nodes"][1:], start=1):
            self.create_node_row_at_index(idx, node)

    def delete_node_row(self, row_frame):
        if len(self.node_entries) == 1:
            return

        index = self.get_node_row_index(row_frame)
        self.node_entries[index][0].grid_forget()
        self.node_entries.pop(index)
        self.refresh_node_grid()

    def refresh_node_grid(self):
        for idx, (frame, label) in enumerate(self.node_entries):
            frame.grid(row=idx + 1, column=0, pady=5)
            label.config(text=f"Узел {idx + 1}")

    def get_node_row_index(self, row_frame):
        for idx, (frame, label) in enumerate(self.node_entries):
            if frame == row_frame:
                return idx
        return -1

    def get_node_entries(self):
        node_vals = []
        for frame, label in self.node_entries:
            node_entry = frame.grid_slaves(row=0, column=1)[0]
            node_val = node_entry.get()
            node_vals.append(node_val)
        self.user_input["nodes"] = node_vals

    def reset_node_entries(self):
        for frame, label in self.node_entries:
            frame.grid_forget()
        self.node_entries.clear()
        self.create_node_row()
        self.refresh_node_grid()

    def initialize_bars_section(self):
        canvas = tk.Canvas(self.bars_frame, width=500, height=150)
        canvas.grid(row=0, column=0, columnspan=8, sticky='nsew')

        scrollbar = tk.Scrollbar(self.bars_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=8, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_bar_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_bar_frame, anchor="nw")

        self.scrollable_bar_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(self.scrollable_bar_frame, text="                       "
                                                 "узел 1             "
                                                 "узел 2             "
                                                 "A, м^2              "
                                                 "E, Па              "
                                                 "[σ], Па").grid(row=0, column=2, sticky='ew')
        self.bar_entries = []
        self.bar_input_data = []
        self.create_bar_row()

    def create_bar_row(self):
        row_index = len(self.bar_entries) + 1

        self.first_bar_frame = tk.Frame(self.scrollable_bar_frame)
        self.first_bar_frame.grid(row=row_index, column=0, columnspan=8, pady=2, sticky="ew")

        bar_label = tk.Label(self.first_bar_frame, text=f"Стержень {row_index}:")
        bar_label.grid(row=0, column=0, padx=5)

        first_node = tk.Entry(self.first_bar_frame, width=5, validate='all', validatecommand=self.bar_node_check)
        first_node.grid(row=0, column=1, padx=20)
        second_node = tk.Entry(self.first_bar_frame, width=5, validate='all', validatecommand=self.bar_node_check)
        second_node.grid(row=0, column=2, padx=20)
        a = tk.Entry(self.first_bar_frame, width=5, validate='all', validatecommand=self.bar_a_check)
        a.grid(row=0, column=3, padx=20)
        e = tk.Entry(self.first_bar_frame, width=5, validate='all', validatecommand=self.bar_e_check)
        e.grid(row=0, column=4, padx=20)
        max_load = tk.Entry(self.first_bar_frame, width=5, validate='all', validatecommand=self.bar_max_load_check)
        max_load.grid(row=0, column=5, padx=20)

        add_button = tk.Button(self.first_bar_frame, text="+", command=lambda: self.add_bar_row(self.first_bar_frame), width=2)
        add_button.grid(row=0, column=6)

        remove_button = tk.Button(self.first_bar_frame, text="-", command=lambda: self.delete_bar_row(self.first_bar_frame), width=2)
        remove_button.grid(row=0, column=7)

        self.bar_entries.append((self.first_bar_frame, bar_label))
        self.bar_input_data.append({
            'first_node': first_node,
            'second_node': second_node,
            'a': a,
            'e': e,
            'max_load': max_load
        })
        self.refresh_bar_grid()

    def add_bar_row(self, row_frame):
        index = self.get_bar_row_index(row_frame)
        self.create_bar_row_at_index(index + 1)

    def create_bar_row_at_index(self, index, node1_val=None, node2_val=None, a_val=None, e_val=None, max_load_val=None):
        frame = tk.Frame(self.scrollable_bar_frame)
        frame.grid(row=index + 1, column=0, columnspan=8, pady=2, sticky="ew")

        bar_label = tk.Label(frame, text=f"Стержень {index + 1}:")
        bar_label.grid(row=0, column=0, padx=5)

        first_node = tk.Entry(frame, width=5, validate='all', validatecommand=self.bar_node_check)
        first_node.grid(row=0, column=1, padx=20)
        second_node = tk.Entry(frame, width=5, validate='all', validatecommand=self.bar_node_check)
        second_node.grid(row=0, column=2, padx=20)
        a = tk.Entry(frame, width=5, validate='all', validatecommand=self.bar_a_check)
        a.grid(row=0, column=3, padx=20)
        e = tk.Entry(frame, width=5, validate='all', validatecommand=self.bar_e_check)
        e.grid(row=0, column=4, padx=20)
        max_load = tk.Entry(frame, width=5, validate='all', validatecommand=self.bar_max_load_check)
        max_load.grid(row=0, column=5, padx=20)

        if node1_val is not None:
            first_node.insert(0, node1_val)
        if node2_val is not None:
            second_node.insert(0, node2_val)
        if a_val is not None:
            a.insert(0, a_val)
        if e_val is not None:
            e.insert(0, e_val)
        if max_load_val is not None:
            max_load.insert(0, max_load_val)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_bar_row(frame), width=2)
        add_button.grid(row=0, column=6)

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_bar_row(frame), width=2)
        remove_button.grid(row=0, column=7)

        self.bar_entries.insert(index, (frame, bar_label))
        self.bar_input_data.append({
            'first_node': first_node,
            'second_node': second_node,
            'a': a,
            'e': e,
            'max_load': max_load
        })
        self.refresh_bar_grid()

    def fill_bars(self):
        for idx, node_dict in enumerate(self.user_input["bars"]):
            self.create_bar_row_at_index(idx+1, node_dict["first_node"], node_dict["second_node"], node_dict["a"], node_dict["e"], node_dict["max_load"])

    def delete_bar_row(self, row_frame):
        if len(self.bar_entries) == 1:
            return

        index = self.get_bar_row_index(row_frame)
        self.bar_input_data.pop(index)
        self.bar_entries[index][0].grid_forget()
        self.bar_entries.pop(index)
        self.refresh_bar_grid()

    def refresh_bar_grid(self):
        for idx, (frame, label) in enumerate(self.bar_entries):
            frame.grid(row=idx + 1, column=0, pady=5)
            label.config(text=f"Стержень {idx + 1}")

    def get_bar_row_index(self, row_frame):
        for idx, (frame, label) in enumerate(self.bar_entries):
            if frame == row_frame:
                return idx
        return -1

    def get_bar_entries(self):
        bar_vals = []
        for entry_dict in self.bar_input_data:
            data = {
                'first_node': entry_dict['first_node'].get(),
                'second_node': entry_dict['second_node'].get(),
                'a': entry_dict['a'].get(),
                'e': entry_dict['e'].get(),
                'max_load': entry_dict['max_load'].get(),
            }
            bar_vals.append(data)
        self.user_input["bars"] = bar_vals

    def reset_bar_entries(self):
        for frame, label in self.bar_entries:
            frame.grid_forget()
        self.bar_entries.clear()

        self.refresh_bar_grid()
        self.bar_input_data.clear()

    def initialize_loads_section(self):
        self.conc_load = tk.LabelFrame(self.loads_frame, bd=2, relief="groove", text="Сосредоточенные")
        self.conc_load.grid(row=0, column=0, columnspan=4, sticky='wn')

        canvas = tk.Canvas(self.conc_load, width=180, height=131)
        canvas.grid(row=0, column=0, columnspan=4, sticky='nw')

        scrollbar = tk.Scrollbar(self.conc_load, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=4, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_conc_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_conc_frame, anchor="nw")

        self.scrollable_conc_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        tk.Label(self.scrollable_conc_frame, text="№ узла").grid(row=0, column=0)
        tk.Label(self.scrollable_conc_frame, text="значение").grid(row=0, column=1)

        self.dist_load = tk.LabelFrame(self.loads_frame, bd=2, relief="groove", text="Распределенные")
        self.dist_load.grid(row=0, column=4, columnspan=4, sticky='wn')

        canvas1 = tk.Canvas(self.dist_load, width=180, height=131)
        canvas1.grid(row=0, column=0, columnspan=4, sticky='nw')

        scrollbar1 = tk.Scrollbar(self.dist_load, orient="vertical", command=canvas1.yview)
        scrollbar1.grid(row=0, column=4, sticky='ns')

        canvas1.configure(yscrollcommand=scrollbar1.set)
        self.scrollable_dist_frame = tk.Frame(canvas1)
        canvas1.create_window((0, 0), window=self.scrollable_dist_frame, anchor="nw")

        self.scrollable_dist_frame.bind("<Configure>", lambda e: canvas1.configure(scrollregion=canvas1.bbox("all")))
        tk.Label(self.scrollable_dist_frame, text="№ стержня").grid(row=0, column=0, sticky='w')
        tk.Label(self.scrollable_dist_frame, text="значение").grid(row=0, column=1, sticky='w')

        self.conc_load_entries = []
        self.conc_load_input_data = []
        self.create_conc_load_row()

        self.dist_load_entries = []
        self.dist_load_input_data = []
        self.create_dist_load_row()

    def create_conc_load_row(self):
        row_index = len(self.conc_load_entries) + 1

        self.first_conc_load_frame = tk.Frame(self.scrollable_conc_frame)
        self.first_conc_load_frame.grid(row=row_index, column=0, columnspan=4, pady=2)

        node_num = tk.Entry(self.first_conc_load_frame, width=5, validate='all', validatecommand=self.node_check)
        node_num.grid(row=0, column=0, padx=15)

        conc_load = tk.Entry(self.first_conc_load_frame, width=5, validate='all', validatecommand=self.loads_check)
        conc_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(self.first_conc_load_frame, text="+", command=lambda: self.add_conc_load_row(self.first_conc_load_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(self.first_conc_load_frame, text="-", command=lambda: self.delete_conc_load_row(self.first_conc_load_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.conc_load_entries.append(self.first_conc_load_frame)
        self.conc_load_input_data.append({
            "node_num": node_num,
            "conc_load": conc_load
        })
        self.refresh_conc_load_grid()

    def add_conc_load_row(self, row_frame):
        index = self.get_conc_load_row_index(row_frame)
        self.create_conc_row_at_index(index + 1)

    def create_conc_row_at_index(self, index, node_val=None, conc_load_val=None):
        row_frame = tk.Frame(self.scrollable_conc_frame)
        row_frame.grid(row=index + 1, column=0, columnspan=4, pady=2)

        node_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        node_num.grid(row=0, column=0, padx=15)

        conc_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        conc_load.grid(row=0, column=1, padx=15)

        if node_val is not None:
            node_num.insert(0, node_val)
        if conc_load_val is not None:
            conc_load.insert(0, conc_load_val)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_conc_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_conc_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.conc_load_entries.insert(index, row_frame)
        self.conc_load_input_data.append({
            "node_num": node_num,
            "conc_load": conc_load
        })
        self.refresh_conc_load_grid()

    def fill_conc_load(self):
        for idx, conc_dict in enumerate(self.user_input["conc_loads"]):
            self.create_conc_row_at_index(idx+1, conc_dict["node_num"], conc_dict["conc_load"])

    def delete_conc_load_row(self, row_frame):
        if len(self.conc_load_entries) == 1:
            return

        index = self.get_conc_load_row_index(row_frame)
        self.conc_load_input_data.pop(index)
        self.conc_load_entries[index].grid_forget()
        self.conc_load_entries.pop(index)
        self.refresh_conc_load_grid()

    def refresh_conc_load_grid(self):
        for idx, frame in enumerate(self.conc_load_entries):
            frame.grid(row=idx + 1, column=0, pady=5)

    def get_conc_load_row_index(self, row_frame):
        for idx, frame in enumerate(self.conc_load_entries):
            if frame == row_frame:
                return idx
        return -1

    def get_conc_load_entries(self):
        conc_load_vals = []
        for entry_dict in self.conc_load_input_data:
            data = {
                "node_num": entry_dict["node_num"].get(),
                "conc_load": entry_dict["conc_load"].get()
            }
            conc_load_vals.append(data)
        self.user_input["conc_loads"] = conc_load_vals

    def reset_conc_load_entries(self):
        for frame in self.conc_load_entries:
            frame.grid_forget()
        self.conc_load_entries.clear()
        self.refresh_conc_load_grid()
        self.conc_load_input_data.clear()

    def create_dist_load_row(self):
        row_index = len(self.dist_load_entries) + 1

        self.first_dist_load_frame = tk.Frame(self.scrollable_dist_frame)
        self.first_dist_load_frame.grid(row=row_index, column=0, columnspan=4, pady=2)

        bar_num = tk.Entry(self.first_dist_load_frame, width=5, validate='all', validatecommand=self.node_check)
        bar_num.grid(row=0, column=0, padx=15)

        dist_load = tk.Entry(self.first_dist_load_frame, width=5, validate='all', validatecommand=self.loads_check)
        dist_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(self.first_dist_load_frame, text="+", command=lambda: self.add_dist_load_row(self.first_dist_load_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(self.first_dist_load_frame, text="-", command=lambda: self.delete_dist_load_row(self.first_dist_load_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.dist_load_entries.append(self.first_dist_load_frame)
        self.dist_load_input_data.append({
            "bar_num": bar_num,
            "dist_load": dist_load
        })
        self.refresh_dist_load_grid()

    def add_dist_load_row(self, row_frame):
        index = self.get_dist_load_row_index(row_frame)
        self.create_dist_row_at_index(index + 1)

    def create_dist_row_at_index(self, index, bar_val=None, dist_load_val=None):
        row_frame = tk.Frame(self.scrollable_dist_frame)
        row_frame.grid(row=index + 1, column=0, columnspan=4, pady=2)

        bar_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        bar_num.grid(row=0, column=0, padx=15)

        dist_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        dist_load.grid(row=0, column=1, padx=15)

        if bar_val is not None:
            bar_num.insert(0, bar_val)
        if dist_load_val is not None:
            dist_load.insert(0, dist_load_val)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_dist_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_dist_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.dist_load_entries.insert(index, row_frame)
        self.dist_load_input_data.append({
            "bar_num": bar_num,
            "dist_load": dist_load
        })
        self.refresh_dist_load_grid()

    def fill_dist_load(self):
        for idx, dist_dict in enumerate(self.user_input["dist_loads"]):
            self.create_dist_row_at_index(idx+1, dist_dict["bar_num"], dist_dict["dist_load"])

    def delete_dist_load_row(self, row_frame):
        if len(self.dist_load_entries) == 1:
            return

        index = self.get_dist_load_row_index(row_frame)
        self.dist_load_input_data.pop(index)
        self.dist_load_entries[index].grid_forget()
        self.dist_load_entries.pop(index)
        self.refresh_dist_load_grid()

    def refresh_dist_load_grid(self):
        for idx, frame in enumerate(self.dist_load_entries):
            frame.grid(row=idx + 1, column=0, pady=5)

    def get_dist_load_row_index(self, row_frame):
        for idx, frame in enumerate(self.dist_load_entries):
            if frame == row_frame:
                return idx
        return -1

    def get_dist_load_entries(self):
        dist_load_vals = []
        for entry_dict in self.dist_load_input_data:
            data = {
                "bar_num": entry_dict["bar_num"].get(),
                "dist_load": entry_dict["dist_load"].get()
            }
            dist_load_vals.append(data)
        self.user_input["dist_loads"] = dist_load_vals

    def reset_dist_load_entries(self):
        for frame in self.dist_load_entries:
            frame.grid_forget()
        self.dist_load_entries.clear()
        self.refresh_dist_load_grid()
        self.dist_load_input_data.clear()

    def initialize_preview_section(self):
        self.preview_canvas = tk.Canvas(self.preview_frame, width=675, height=300, bg="white", bd=1, relief="sunken")
        self.preview_canvas.grid(row=1, column=0, columnspan=6, pady=5, padx=10)

        preview_button = tk.Button(self.preview_frame, text="Предпросмотр", command=lambda: self.show_scheme())
        preview_button.grid(row=0, column=0, sticky='w', padx=10)

        zadelka_label = tk.Label(self.preview_frame, text="Установить заделку:")
        zadelka_label.grid(row=0, column=4, sticky='e', padx=10)

        self.left_zad = tk.IntVar(value=1)
        self.right_zad = tk.IntVar(value=0)

        left_zadelka = tk.Checkbutton(self.preview_frame, variable=self.left_zad, text="слева", command=lambda: self.on_check("cb1"))
        left_zadelka.grid(row=0, column=5, sticky='w')

        right_zadelka = tk.Checkbutton(self.preview_frame, variable=self.right_zad, text="справа", command=lambda: self.on_check("cb2"))
        right_zadelka.grid(row=0, column=5, sticky='e', padx=10)

    def on_check(self, sender_widget):
        if not self.left_zad.get() and not self.right_zad.get():
            if sender_widget == 'cb1':
                self.right_zad.set(1)
            elif sender_widget == 'cb2':
                self.left_zad.set(1)

    def initialize_postprocess_section(self):
        build_tables_button = tk.Button(self.postprocess_frame, text="Построение таблиц", width=30)
        build_tables_button.pack(pady=15)

        build_graphs_button = tk.Button(self.postprocess_frame, text="Построение графиков", width=30)
        build_graphs_button.pack(pady=15)

        build_diagrams_button = tk.Button(self.postprocess_frame, text="Построение эпюр", width=30)
        build_diagrams_button.pack(pady=15)

        section_analysis_button = tk.Button(self.postprocess_frame, text="Анализ сечения", width=30)
        section_analysis_button.pack(pady=15)

        generate_file_button = tk.Button(self.postprocess_frame, text="Сформировать файл", width=30)
        generate_file_button.pack(pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = SaprApp(root)
    root.mainloop()
