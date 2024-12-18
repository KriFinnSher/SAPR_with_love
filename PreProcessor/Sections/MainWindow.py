import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PreProcessor.Service import Drawing, InputChecker, Scaler, Validators
from Processor import MainProcessing
from collections import defaultdict
from tkinter import messagebox
from PostProcessor import TablesCreation, Epura, FileGeneration
from PreProcessor.Sections.TemplateSections import NodeSection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class SaprApp:

    def __init__(self, root):
        self.root = root

        style = ttk.Style(root)
        style.theme_use("alt")
        style.configure(
            "Custom.Vertical.TScrollbar",
            troughcolor="#f0dcc0",
            background="#f5d4a4",
        )
        style.map(
            "Custom.Vertical.TScrollbar",
            background=[('active', '#fac982')]
        )
        style.configure("TNotebook", background="#fceac5")
        style.configure("TNotebook.Tab", background="#f5d4a4", foreground="#000")
        style.map("TNotebook.Tab",
                  background=[("selected", "#f7ce92")],
                  foreground=[("selected", "white")])

        self.root.title("SAPR with love")
        root.option_add('*tearOff', 0)
        root.configure(bg="#b7e8c5")

        self.root.geometry("1140x570")
        self.root.resizable(False, False)

        self.user_input = defaultdict(list)
        self.last_files = []

        self.node_check = (self.root.register(Validators.rational_positive_number), '%P')
        self.bar_node_check = (self.root.register(Validators.natural_positive_number), '%P')
        self.bar_a_check = (self.root.register(Validators.rational_positive_number), '%P')
        self.bar_e_check = (self.root.register(Validators.rational_positive_number), '%P')
        self.bar_max_load_check = (self.root.register(Validators.rational_positive_number), '%P')
        self.loads_check = (self.root.register(Validators.rational_number), '%P')

        self.nodes_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление узлов")
        self.nodes_frame.configure(bg="#f0dcc0")
        self.bars_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление стержней")
        self.bars_frame.configure(bg="#f0dcc0")
        self.loads_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Добавление нагрузок")
        self.loads_frame.configure(bg="#f0dcc0")
        self.preview_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Полученная схема")
        self.preview_frame.configure(bg="#f0dcc0")
        self.postprocess_frame = tk.LabelFrame(root, bd=2, relief="groove", text="Данные постпроцессора")
        self.postprocess_frame.configure(bg="#f0dcc0")

        self.nodes_frame.grid(row=0, column=0, padx=5, pady=10, sticky="n")
        self.bars_frame.grid(row=0, column=1, padx=5, pady=10, sticky="n")
        self.loads_frame.grid(row=0, column=2, padx=5, pady=10, sticky="n")
        self.preview_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        self.postprocess_frame.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")

        self.node_section = NodeSection.NodeApp(root)
        self.node_section.init_section(self.nodes_frame)

        self.initialize_bars_section()
        self.initialize_loads_section()
        self.initialize_preview_section()
        self.initialize_postprocess_section()
        self.initialize_menu_section()

    def refresh(self):
        self.node_section.get_row_values(self.user_input)
        self.get_bar_entries()
        self.get_conc_load_entries()
        self.get_dist_load_entries()
        self.get_zadelki()


    def show_scheme(self, for_file=False):
        self.refresh()
        if InputChecker.input_is_correct(self.user_input):
            self.user_input["nodes"] = [0] + Scaler.scale_to_k(self.user_input["nodes"][1:], 10)
            lengths = [float(val) for val in self.user_input["nodes"][1:]]
            nodes = [0.] * len(self.node_section.entries)
            for i in range(1, len(self.node_section.entries)):
                nodes[i] = float(self.user_input["nodes"][i]) + nodes[i-1]
            heights = [0.] * len(self.bar_entries)

            for bar in self.user_input["bars"]:
                heights[max(int(bar["second_node"]), int(bar["first_node"])) - 2] = float(bar["a"])
            heights = Scaler.scale_to_k(heights, 10)
            self.sheme = Drawing.display_scheme(self.preview_canvas, lengths, heights, self.user_input["bars"], nodes,
                                   self.user_input["conc_loads"], self.user_input["dist_loads"],
                                   self.user_input['left_zadelka'], self.user_input['right_zadelka'], for_file)

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

            self.node_section.fill_section(self.user_input, "nodes")
            self.fill_bars()
            self.fill_conc_load()
            self.fill_dist_load()
            self.fill_zadelki()

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

            self.node_section.fill_section(self.user_input, "nodes")
            self.fill_bars()
            self.fill_conc_load()
            self.fill_dist_load()
            self.fill_zadelki()

    def reset_input_for_file(self):
        self.node_section.reset_values()
        self.reset_bar_entries()
        self.reset_conc_load_entries()
        self.reset_dist_load_entries()

        self.preview_canvas.delete("all")

    def reset_input(self):
        self.node_section.reset_values()
        self.reset_bar_entries()
        self.reset_conc_load_entries()
        self.reset_dist_load_entries()

        self.create_bar_row()
        self.create_conc_load_row()
        self.create_dist_load_row()

        self.preview_canvas.delete("all")



    def initialize_bars_section(self):
        canvas = tk.Canvas(self.bars_frame, width=500, height=150)
        canvas.grid(row=0, column=0, columnspan=8, sticky='nsew')
        canvas.configure(bg="#fceac5")

        scrollbar = ttk.Scrollbar(self.bars_frame, orient="vertical", command=canvas.yview, style='Custom.Vertical.TScrollbar')
        scrollbar.grid(row=0, column=8, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_bar_frame = tk.Frame(canvas)
        self.scrollable_bar_frame.configure(bg="#fceac5")
        canvas.create_window((0, 0), window=self.scrollable_bar_frame, anchor="nw")

        self.scrollable_bar_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        a = (tk.Label(self.scrollable_bar_frame, text="                       "
                                                 "узел 1             "
                                                 "узел 2             "
                                                 "A, м^2              "
                                                 "E, Па              "
                                                 "[σ], Па"))
        a.grid(row=0, column=2, sticky='ew')
        a.configure(bg="#fceac5")
        self.bar_entries = []
        self.bar_input_data = []
        self.create_bar_row()

    def create_bar_row(self):
        row_index = len(self.bar_entries) + 1

        self.first_bar_frame = tk.Frame(self.scrollable_bar_frame)
        self.first_bar_frame.grid(row=row_index, column=0, columnspan=8, pady=2, sticky="ew")
        self.first_bar_frame.configure(bg="#fceac5")

        bar_label = tk.Label(self.first_bar_frame, text=f"Стержень {row_index}:")
        bar_label.grid(row=0, column=0, padx=5)
        bar_label.configure(bg="#fceac5")

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

        add_button = tk.Button(self.first_bar_frame, text="+",
                               command=lambda: self.add_bar_row(self.first_bar_frame), width=2)
        add_button.grid(row=0, column=6)
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        remove_button = tk.Button(self.first_bar_frame, text="-",
                                  command=lambda: self.delete_bar_row(self.first_bar_frame), width=2)
        remove_button.grid(row=0, column=7)
        remove_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

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
        frame.configure(bg="#fceac5")

        bar_label = tk.Label(frame, text=f"Стержень {index + 1}:")
        bar_label.grid(row=0, column=0, padx=5)
        bar_label.configure(bg="#fceac5")

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
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_bar_row(frame), width=2)
        remove_button.grid(row=0, column=7)
        remove_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        self.bar_entries.insert(index, (frame, bar_label))
        self.bar_input_data.insert(index, {
            'first_node': first_node,
            'second_node': second_node,
            'a': a,
            'e': e,
            'max_load': max_load
        })
        self.refresh_bar_grid()

    def fill_bars(self):
        for idx, node_dict in enumerate(self.user_input["bars"]):
            self.create_bar_row_at_index(idx+1, node_dict["first_node"], node_dict["second_node"],
                                         node_dict["a"], node_dict["e"], node_dict["max_load"])

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
        self.conc_load.configure(bg="#fceac5")

        canvas = tk.Canvas(self.conc_load, width=180, height=131)
        canvas.grid(row=0, column=0, columnspan=4, sticky='nw')
        canvas.configure(bg="#fceac5")

        scrollbar = ttk.Scrollbar(self.conc_load, orient="vertical", command=canvas.yview, style='Custom.Vertical.TScrollbar')
        scrollbar.grid(row=0, column=4, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_conc_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_conc_frame, anchor="nw")
        self.scrollable_conc_frame.configure(bg="#fceac5")

        self.scrollable_conc_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        a = tk.Label(self.scrollable_conc_frame, text="№ узла")
        a.grid(row=0, column=0)
        a.configure(bg="#fceac5")
        b = tk.Label(self.scrollable_conc_frame, text="значение")
        b.grid(row=0, column=1)
        b.configure(bg="#fceac5")

        self.dist_load = tk.LabelFrame(self.loads_frame, bd=2, relief="groove", text="Распределенные")
        self.dist_load.grid(row=0, column=4, columnspan=4, sticky='wn')
        self.dist_load.configure(bg="#fceac5")

        canvas1 = tk.Canvas(self.dist_load, width=180, height=131)
        canvas1.grid(row=0, column=0, columnspan=4, sticky='nw')
        canvas1.configure(bg="#fceac5")

        scrollbar1 = ttk.Scrollbar(self.dist_load, orient="vertical", command=canvas1.yview, style='Custom.Vertical.TScrollbar')
        scrollbar1.grid(row=0, column=4, sticky='ns')

        canvas1.configure(yscrollcommand=scrollbar1.set)
        self.scrollable_dist_frame = tk.Frame(canvas1)
        self.scrollable_dist_frame.configure(bg="#fceac5")
        canvas1.create_window((0, 0), window=self.scrollable_dist_frame, anchor="nw")

        self.scrollable_dist_frame.bind("<Configure>", lambda e: canvas1.configure(scrollregion=canvas1.bbox("all")))
        c = tk.Label(self.scrollable_dist_frame, text="№ стержня")
        c.grid(row=0, column=0, sticky='w')
        c.configure(bg="#fceac5")
        d = tk.Label(self.scrollable_dist_frame, text="значение")
        d.grid(row=0, column=1, sticky='w')
        d.configure(bg="#fceac5")

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
        self.first_conc_load_frame.configure(bg="#fceac5")

        node_num = tk.Entry(self.first_conc_load_frame, width=5, validate='all', validatecommand=self.node_check)
        node_num.grid(row=0, column=0, padx=15)

        conc_load = tk.Entry(self.first_conc_load_frame, width=5, validate='all', validatecommand=self.loads_check)
        conc_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(self.first_conc_load_frame, text="+",
                               command=lambda: self.add_conc_load_row(self.first_conc_load_frame), width=2)
        add_button.grid(row=0, column=2)
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        delete_button = tk.Button(self.first_conc_load_frame, text="-",
                                  command=lambda: self.delete_conc_load_row(self.first_conc_load_frame), width=2)
        delete_button.grid(row=0, column=3)
        delete_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

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
        row_frame.configure(bg="#fceac5")

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
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_conc_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)
        delete_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        self.conc_load_entries.insert(index, row_frame)
        self.conc_load_input_data.insert(index, {
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
        self.first_dist_load_frame.configure(bg="#fceac5")

        bar_num = tk.Entry(self.first_dist_load_frame, width=5, validate='all', validatecommand=self.node_check)
        bar_num.grid(row=0, column=0, padx=15)

        dist_load = tk.Entry(self.first_dist_load_frame, width=5, validate='all', validatecommand=self.loads_check)
        dist_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(self.first_dist_load_frame, text="+",
                               command=lambda: self.add_dist_load_row(self.first_dist_load_frame), width=2)
        add_button.grid(row=0, column=2)
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        delete_button = tk.Button(self.first_dist_load_frame, text="-",
                                  command=lambda: self.delete_dist_load_row(self.first_dist_load_frame), width=2)
        delete_button.grid(row=0, column=3)
        delete_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

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
        row_frame.configure(bg="#fceac5")

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
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_dist_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)
        delete_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        self.dist_load_entries.insert(index, row_frame)
        self.dist_load_input_data.insert(index, {
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
        self.preview_canvas.configure(bg='#b7e8c5')

        preview_button = tk.Button(self.preview_frame, text="Предпросмотр", command=lambda: self.show_scheme())
        preview_button.grid(row=0, column=0, sticky='w', padx=10)
        preview_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        zadelka_label = tk.Label(self.preview_frame, text="Установить заделку:")
        zadelka_label.grid(row=0, column=4, sticky='e', padx=10)
        zadelka_label.configure(bg="#f0dcc0")

        self.left_zad = tk.IntVar(value=1)
        self.right_zad = tk.IntVar(value=0)

        left_zadelka = tk.Checkbutton(self.preview_frame, variable=self.left_zad, text="слева",
                                      command=lambda: self.on_check("cb1"))
        left_zadelka.grid(row=0, column=5, sticky='w')
        left_zadelka.configure(bg="#f0dcc0", activebackground="#f0dcc0")

        right_zadelka = tk.Checkbutton(self.preview_frame, variable=self.right_zad, text="справа",
                                       command=lambda: self.on_check("cb2"))
        right_zadelka.grid(row=0, column=5, sticky='e', padx=10)
        right_zadelka.configure(bg="#f0dcc0", activebackground="#f0dcc0")

    def on_check(self, sender_widget):
        if not self.left_zad.get() and not self.right_zad.get():
            if sender_widget == 'cb1':
                self.right_zad.set(1)
            elif sender_widget == 'cb2':
                self.left_zad.set(1)

        self.user_input['left_zadelka'] = [1] if self.left_zad.get() else [0]
        self.user_input['right_zadelka'] = [1] if self.right_zad.get() else [0]

    def get_zadelki(self):
        self.user_input['left_zadelka'] = [1] if self.left_zad.get() else [0]
        self.user_input['right_zadelka'] = [1] if self.right_zad.get() else [0]

    def fill_zadelki(self):
        self.left_zad.set(self.user_input['left_zadelka'][0])
        self.right_zad.set(self.user_input['right_zadelka'][0])



    def initialize_postprocess_section(self):
        build_tables_button = tk.Button(self.postprocess_frame, text="Построение таблиц", width=30, command=self.show_tables)
        build_tables_button.pack(pady=(55,15))
        build_tables_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        build_diagrams_button = tk.Button(self.postprocess_frame, text="Построение эпюр", width=30, command=self.show_epuras)
        build_diagrams_button.pack(pady=15)
        build_diagrams_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        section_analysis_button = tk.Button(self.postprocess_frame, text="Анализ сечения", width=30, command=self.section_calc_window)
        section_analysis_button.pack(pady=15)
        section_analysis_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        generate_file_button = tk.Button(self.postprocess_frame, text="Сформировать файл", width=30, command=self.generate_file)
        generate_file_button.pack(pady=15)
        generate_file_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

    def section_calc_window(self):
        window = tk.Tk()
        window.title("Ввод данных")

        rat_pos_checker = (window.register(Validators.rational_positive_number), '%P')
        nat_pos_checker = (window.register(Validators.natural_positive_number), '%P')

        window.geometry("220x170")

        window.resizable(False, False)

        label1 = tk.Label(window, text="№ стержня:")
        label1.grid(row=0, column=0, padx=5, pady=5)
        label1.configure(bg="#f0dcc0")

        self.bar_num = tk.Entry(window, width=5, validate='all', validatecommand=nat_pos_checker)
        self.bar_num.grid(row=0, column=1, padx=10, pady=5)

        label2 = tk.Label(window, text="x:")
        label2.grid(row=0, column=2, padx=11, pady=5)
        label2.configure(bg="#f0dcc0")

        self.x = tk.Entry(window, width=5, validate='all', validatecommand=rat_pos_checker)
        self.x.grid(row=0, column=3, padx=5, pady=5)

        button = tk.Button(window, text="Рассчитать", command=self.section_calc)
        button.grid(row=1, column=0, columnspan=4, pady=10)
        button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        res_label = tk.Label(window, text="Результаты:")
        res_label.grid(row=2, column=0, padx=5, pady=5)
        res_label.configure(bg="#f0dcc0")

        self.u_label = tk.Label(window, text="U(x) = -")
        self.u_label.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        self.u_label.configure(bg="#f0dcc0")

        self.n_label = tk.Label(window, text="N(x) = -")
        self.n_label.grid(row=3, column=1, columnspan=2, padx=5, pady=5)
        self.n_label.configure(bg="#f0dcc0")

        self.sigma_label = tk.Label(window, text="σ(x) = -")
        self.sigma_label.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        self.sigma_label.configure(bg="#f0dcc0")

        self.window = window
        self.window.configure(background="#f0dcc0")

    def section_calc(self):
        self.refresh()
        data = self.user_input
        if InputChecker.input_is_correct(data):
            if self.x.get() == '' or self.bar_num.get() == '':
                messagebox.showwarning("Ошибка ввода данных", "Заполните оба поля в окне")
                return
            else:
                if not (1 <= int(self.bar_num.get()) <= len(self.user_input['bars'])):
                    messagebox.showwarning("Ошибка ввода данных", "Указан несуществующий стержень")
                    return

                x = float(self.x.get())
                bar_num = int(self.bar_num.get())
                l = int(data['nodes'][bar_num])

                if not (0 <= x <= l):
                    messagebox.showwarning("Ошибка ввода данных", "Координата x должна быть в пределах стержня")
                    return

                u, n, sigma = MainProcessing.section_calc_for_window(self)

                self.u_label.config(text=f"U(x) = {u}")
                self.n_label.config(text=f"N(x) = {n}")

                sigma_max = next((float(bar['max_load']) for bar in data['bars'] if
                                  min(int(bar['first_node']), int(bar['second_node'])) == bar_num), 0)
                if abs(sigma) > abs(sigma_max):
                    self.sigma_label.config(text=f"σ(x) = {sigma}", fg='red')
                else:
                    self.sigma_label.config(text=f"σ(x) = {sigma}")


    def show_tables(self):
        self.refresh()
        data = self.user_input

        if InputChecker.input_is_correct(data):
            TablesCreation.display_tables(data)


    def show_epuras(self):
        self.refresh()
        data = self.user_input
        if InputChecker.input_is_correct(data):

            epura_window = tk.Toplevel(self.root)
            epura_window.title("Эпюры")
            epura_window.geometry("800x600")
            epura_window.resizable(False, False)

            notebook = ttk.Notebook(epura_window, style="TNotebook")
            notebook.pack(expand=True, fill="both")

            tab_u = ttk.Frame(notebook)
            tab_n = ttk.Frame(notebook)
            tab_sigma = ttk.Frame(notebook)

            notebook.add(tab_u, text='Эпюра U(x)')
            notebook.add(tab_n, text='Эпюра N(x)')
            notebook.add(tab_sigma, text='Эпюра σ(x)')

            def create_canvas_and_draw(tab, draw_function, *args):
                canvas = tk.Canvas(tab)
                canvas.pack(expand=True, fill='both')
                fig = plt.figure()
                draw_function(*args)
                canvas_widget = FigureCanvasTkAgg(fig, master=canvas)
                canvas_widget.draw()
                canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            create_canvas_and_draw(tab_u, Epura.draw_epur_u, data)

            x_coords, y_coords_nx, y_coords_sigma = MainProcessing.section_calc_for_nx_epur(data)
            create_canvas_and_draw(tab_n, Epura.draw_epur_n_sigma, x_coords, y_coords_nx, "N")
            create_canvas_and_draw(tab_sigma, Epura.draw_epur_n_sigma, x_coords, y_coords_sigma, "σ")


    def generate_file(self):
        self.refresh()
        data = self.user_input
        self.show_scheme(for_file=True)

        if InputChecker.input_is_correct(data):
            FileGeneration.create_file(data, self.sheme)


