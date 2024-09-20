import tkinter as tk
import validators


class SaprApp:

    def __init__(self, root):
        self.root = root
        self.root.title("SAPR with love")

        self.root.geometry("1140x570")
        self.root.resizable(False, False)

        self.node_check = (self.root.register(validators.natural_positive_number), '%P')
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

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_node_row(frame), width=2)
        remove_button.grid(row=0, column=3)

        self.node_entries.append((frame, node_label))
        self.refresh_node_grid()

    def add_node_row(self, row_frame):
        index = self.get_node_row_index(row_frame)
        self.create_node_row_at_index(index + 1)

    def create_node_row_at_index(self, index):
        frame = tk.Frame(self.scrollable_frame)
        frame.grid(row=index + 1, column=0, columnspan=4, pady=2, sticky="ew")

        node_label = tk.Label(frame, text=f"Узел {index + 1}:")
        node_label.grid(row=0, column=0, padx=5, sticky="w")

        node_entry = tk.Entry(frame, width=3, validate='all', validatecommand=self.node_check)
        node_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_node_row(frame), width=2)
        add_button.grid(row=0, column=2)

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_node_row(frame), width=2)
        remove_button.grid(row=0, column=3)

        self.node_entries.insert(index, (frame, node_label))
        self.refresh_node_grid()

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
        self.create_bar_row()

    def create_bar_row(self):
        row_index = len(self.bar_entries) + 1

        frame = tk.Frame(self.scrollable_bar_frame)
        frame.grid(row=row_index, column=0, columnspan=8, pady=2, sticky="ew")

        bar_label = tk.Label(frame, text=f"Стержень {row_index}:")
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

        add_button = tk.Button(frame, text="+", command=lambda: self.add_bar_row(frame), width=2)
        add_button.grid(row=0, column=6)

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_bar_row(frame), width=2)
        remove_button.grid(row=0, column=7)

        self.bar_entries.append((frame, bar_label))
        self.refresh_bar_grid()

    def add_bar_row(self, row_frame):
        index = self.get_bar_row_index(row_frame)
        self.create_bar_row_at_index(index + 1)

    def create_bar_row_at_index(self, index):
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

        add_button = tk.Button(frame, text="+", command=lambda: self.add_bar_row(frame), width=2)
        add_button.grid(row=0, column=6)

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_bar_row(frame), width=2)
        remove_button.grid(row=0, column=7)

        self.bar_entries.insert(index, (frame, bar_label))
        self.refresh_bar_grid()

    def delete_bar_row(self, row_frame):
        if len(self.bar_entries) == 1:
            return

        index = self.get_bar_row_index(row_frame)
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
        self.create_conc_load_row()

        self.dist_load_entries = []
        self.create_dist_load_row()

    def create_conc_load_row(self):
        row_index = len(self.conc_load_entries) + 1

        row_frame = tk.Frame(self.scrollable_conc_frame)
        row_frame.grid(row=row_index, column=0, columnspan=4, pady=2)

        node_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        node_num.grid(row=0, column=0, padx=15)

        conc_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        conc_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_conc_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_conc_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.conc_load_entries.append(row_frame)
        self.refresh_conc_load_grid()

    def add_conc_load_row(self, row_frame):
        index = self.get_conc_load_row_index(row_frame)
        self.create_conc_row_at_index(index + 1)

    def create_conc_row_at_index(self, index):
        row_frame = tk.Frame(self.scrollable_conc_frame)
        row_frame.grid(row=index + 1, column=0, columnspan=4, pady=2)

        node_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        node_num.grid(row=0, column=0, padx=15)

        conc_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        conc_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_conc_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_conc_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.conc_load_entries.insert(index, row_frame)
        self.refresh_conc_load_grid()

    def delete_conc_load_row(self, row_frame):
        if len(self.conc_load_entries) == 1:
            return

        row_frame.grid_forget()
        self.conc_load_entries.remove(row_frame)
        self.refresh_conc_load_grid()

    def refresh_conc_load_grid(self):
        for idx, frame in enumerate(self.conc_load_entries):
            frame.grid(row=idx + 1, column=0, pady=5)

    def get_conc_load_row_index(self, row_frame):
        for idx, frame in enumerate(self.conc_load_entries):
            if frame == row_frame:
                return idx
        return -1

    def create_dist_load_row(self):
        row_index = len(self.dist_load_entries) + 1

        row_frame = tk.Frame(self.scrollable_dist_frame)
        row_frame.grid(row=row_index, column=0, columnspan=4, pady=2)

        bar_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        bar_num.grid(row=0, column=0, padx=15)

        dist_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        dist_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_dist_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_dist_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.dist_load_entries.append(row_frame)
        self.refresh_dist_load_grid()

    def add_dist_load_row(self, row_frame):
        index = self.get_dist_load_row_index(row_frame)
        self.create_dist_row_at_index(index + 1)

    def create_dist_row_at_index(self, index):
        row_frame = tk.Frame(self.scrollable_dist_frame)
        row_frame.grid(row=index + 1, column=0, columnspan=4, pady=2)

        bar_num = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.node_check)
        bar_num.grid(row=0, column=0, padx=15)

        dist_load = tk.Entry(row_frame, width=5, validate='all', validatecommand=self.loads_check)
        dist_load.grid(row=0, column=1, padx=15)

        add_button = tk.Button(row_frame, text="+", command=lambda: self.add_dist_load_row(row_frame), width=2)
        add_button.grid(row=0, column=2)

        delete_button = tk.Button(row_frame, text="-", command=lambda: self.delete_dist_load_row(row_frame), width=2)
        delete_button.grid(row=0, column=3)

        self.dist_load_entries.insert(index, row_frame)
        self.refresh_dist_load_grid()

    def delete_dist_load_row(self, row_frame):
        if len(self.dist_load_entries) == 1:
            return

        row_frame.grid_forget()
        self.dist_load_entries.remove(row_frame)
        self.refresh_dist_load_grid()

    def refresh_dist_load_grid(self):
        for idx, frame in enumerate(self.dist_load_entries):
            frame.grid(row=idx + 1, column=0, pady=5)

    def get_dist_load_row_index(self, row_frame):
        for idx, frame in enumerate(self.dist_load_entries):
            if frame == row_frame:
                return idx
        return -1

    def initialize_preview_section(self):
        preview_label = tk.Label(self.preview_frame, text="здесь должна быть схема", width=97, height=20, bg="white", bd=1,
                                      relief="sunken")
        preview_label.grid(row=1, column=0, columnspan=6, pady=5, padx=10)

        preview_button = tk.Button(self.preview_frame, text="Предпросмотр")
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

        buttons = [
            "Построение таблиц", "Построение графиков", "Построение эпюр",
            "Анализ сечения", "Сформировать файл"
        ]

        for btn_text in buttons:
            button = tk.Button(self.postprocess_frame, text=btn_text, width=30)
            button.pack(pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = SaprApp(root)
    root.mainloop()
