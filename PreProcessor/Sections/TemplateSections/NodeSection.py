from PreProcessor.Sections.AbstractSection import SubApp
from PreProcessor.Service import Validators
import tkinter as tk
from tkinter import ttk


class NodeApp(SubApp):
    def __init__(self, root):
        super().__init__(section_type="nodes")
        self.rpn = (root.register(Validators.rational_positive_number), '%P')
        self.npn = (root.register(Validators.natural_positive_number), '%P')
        self.rn = (root.register(Validators.rational_number), '%P')


    def init_section(self, base_frame):
        canvas = tk.Canvas(base_frame, width=140, height=150)
        canvas.grid(row=0, column=0, columnspan=4, sticky='nsew')
        canvas.configure(bg="#fceac5")

        scrollbar = ttk.Scrollbar(base_frame, orient="vertical", command=canvas.yview,
                                  style='Custom.Vertical.TScrollbar')
        scrollbar.grid(row=0, column=4, sticky='ns')

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.configure(bg="#fceac5")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        a = tk.Label(self.scrollable_frame, text="S, м")
        a.grid(row=0, column=2, sticky='w')
        a.configure(bg="#fceac5")

        self.create_row()

    def create_row(self):
        row_index = len(self.entries) + 1

        frame = tk.Frame(self.scrollable_frame)
        frame.grid(row=row_index, column=0, columnspan=4, pady=2, sticky="ew")
        frame.configure(bg="#fceac5")

        node_label = tk.Label(frame, text=f"Узел {row_index}:")
        node_label.grid(row=0, column=0, padx=5, sticky="w")
        node_label.configure(bg="#fceac5")

        node_entry = tk.Entry(frame, width=3)
        node_entry.insert(0, '0')
        node_entry.config(state='readonly')
        node_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_row(frame), width=2)
        add_button.grid(row=0, column=2)
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        remove_button = tk.Button(frame, text="-", width=2)
        remove_button.grid(row=0, column=3)
        remove_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        self.entries.append((frame, node_label))
        self.refresh_section()

    def create_row_at_index(self, index, node_val=None):
        frame = tk.Frame(self.scrollable_frame)
        frame.grid(row=index + 1, column=0, columnspan=4, pady=2, sticky="ew")
        frame.configure(bg="#fceac5")

        node_label = tk.Label(frame, text=f"Узел {index + 1}:")
        node_label.grid(row=0, column=0, padx=5, sticky="w")
        node_label.configure(bg="#fceac5")

        node_entry = tk.Entry(frame, width=3, validate='all', validatecommand=self.rpn)
        node_entry.grid(row=0, column=1, padx=5)

        if node_val is not None:
            node_entry.insert(0, node_val)

        add_button = tk.Button(frame, text="+", command=lambda: self.add_row(frame), width=2)
        add_button.grid(row=0, column=2)
        add_button.configure(bg="#b7e8c5", activebackground='#9ae6af')

        remove_button = tk.Button(frame, text="-", command=lambda: self.delete_row(frame), width=2)
        remove_button.grid(row=0, column=3)
        remove_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

        self.entries.insert(index, (frame, node_label))
        self.refresh_section()

    def refresh_section(self):
        for idx, (frame, label) in enumerate(self.entries):
            frame.grid(row=idx + 1, column=0, pady=5)
            label.config(text=f"Узел {idx + 1}")


    def get_row_values(self, data):
        node_vals = []
        for frame, label in self.entries:
            node_entry = frame.grid_slaves(row=0, column=1)[0]
            node_val = node_entry.get()
            node_vals.append(node_val)
        data["nodes"] = node_vals
