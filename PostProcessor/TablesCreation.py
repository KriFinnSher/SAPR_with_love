import tkinter as tk
from tkinter import ttk
from . import BarsInfo
from PreProcessor.Service import Validators


def create_table(parent, data):
    table_frame = tk.Frame(parent)

    scrollbar = tk.Scrollbar(table_frame, orient="vertical")
    table = ttk.Treeview(
        table_frame,
        columns=("X", "N(x)", "U(x)", "σ(x)", "[σ]"),
        show="headings",
        height=6,
        yscrollcommand=scrollbar.set,
    )
    scrollbar.config(command=table.yview)
    scrollbar.pack(side="right", fill="y")
    table.pack(side="left", fill="both", expand=True)

    table.heading("X", text="X")
    table.heading("N(x)", text="N(x)")
    table.heading("U(x)", text="U(x)")
    table.heading("σ(x)", text="σ(x)")
    table.heading("[σ]", text="[σ]")

    table.column("X", width=70, anchor="center")
    table.column("N(x)", width=70, anchor="center")
    table.column("U(x)", width=70, anchor="center")
    table.column("σ(x)", width=70, anchor="center")
    table.column("[σ]", width=70, anchor="center")

    table.tag_configure("alert", foreground="red")

    for row in data:
        if abs(row[-2]) > abs(row[-1]):
            table.insert("", "end", values=row, tags=("alert",))
        else:
            table.insert("", "end", values=row)

    return table_frame


def display_tables(data):
    def update_tables(step=5):
        step = int(step_entry.get()) if step_entry.get() else step
        tables_data = BarsInfo.get_all(data, step)

        table_listbox.delete(0, tk.END)
        for widget in table_frame.winfo_children():
            widget.destroy()

        for i in range(len(tables_data)):
            table_listbox.insert(tk.END, f"Стержень {i + 1}")

        global stored_data
        stored_data = tables_data
        selection = table_listbox.curselection()
        if selection:
            index = selection[0]
        else:
            index = 0
            table_listbox.selection_set(0)
        display_table(index)

    def display_table(index):
        for widget in table_frame.winfo_children():
            widget.destroy()

        data = stored_data[index]

        table_widget = create_table(table_frame, data)
        table_widget.pack(fill="both", expand=True)

    def on_listbox_select(event):
        selection = table_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        display_table(index)

    window = tk.Tk()
    window.title("Расчетные таблицы")
    window.geometry("600x220")
    window.resizable(False, False)
    window.configure(bg="#fceac5")

    step_checker = (window.register(Validators.natural_positive_number), '%P')

    top_frame = tk.Frame(window)
    top_frame.pack(side="top", fill="x", padx=10, pady=10)
    top_frame.configure(bg="#fceac5")

    step_label = tk.Label(top_frame, text="Множитель детализации:", font=("Arial", 10))
    step_label.pack(side="left", padx=(0, 5))
    step_label.configure(bg="#fceac5")

    step_entry = tk.Entry(top_frame, width=10, validate='all', validatecommand=step_checker)
    step_entry.pack(side="left", padx=(0, 5))
    step_entry.insert(0, "5")

    update_button = tk.Button(top_frame, text="Обновить", command=update_tables)
    update_button.pack(side="left")
    update_button.configure(bg="#f5d4a4", activebackground='#f7ce92')

    middle_frame = tk.Frame(window)
    middle_frame.pack(side="top", fill="both", expand=True)
    middle_frame.configure(bg="#f0dcc0")

    table_listbox = tk.Listbox(middle_frame, width=20, height=20, selectbackground="#f7ce92", selectforeground="black")
    table_listbox.pack(side="left", fill="y", padx=(5, 0))
    table_listbox.configure(bg="#f0dcc0")

    scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=table_listbox.yview)
    table_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="left", fill="y")

    table_frame = tk.Frame(middle_frame)
    table_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    table_listbox.bind("<<ListboxSelect>>", on_listbox_select)

    update_tables(step=5)

    window.mainloop()
