import tkinter as tk
from tkinter import ttk
from . import bars_info
from PreProcessor import validators


def create_table(parent, data):
    table = ttk.Treeview(parent, columns=("X", "N(x)", "U(x)", "σ(x)", "[σ]"), show="headings", height=5)
    table.heading("X", text="X")
    table.heading("N(x)", text="N(x)")
    table.heading("U(x)", text="U(x)")
    table.heading("σ(x)", text="σ(x)")
    table.heading("[σ]", text="[σ]")

    table.column("X", width=100, anchor="center")
    table.column("N(x)", width=100, anchor="center")
    table.column("U(x)", width=100, anchor="center")
    table.column("σ(x)", width=100, anchor="center")
    table.column("[σ]", width=100, anchor="center")

    table.tag_configure("alert", foreground="red")

    for row in data:
        if abs(row[-2]) > abs(row[-1]):
            table.insert("", "end", values=row, tags=("alert",))
        else:
            table.insert("", "end", values=row)

    return table


def display_tables(root):
    def update_tables(step=5):
        for widget in table_frame.winfo_children():
            widget.destroy()

        step = int(step_entry.get()) if step_entry.get() else step

        tables_data = bars_info.get_all(root, step)

        for i, data in enumerate(tables_data):
            label = tk.Label(table_frame, text=f"Стержень {i + 1}", font=("Arial", 10, "bold"))
            label.grid(row=i * 6, column=0, padx=5, pady=5)

            table = create_table(table_frame, data)
            table.grid(row=i * 6 + 1, column=0, padx=5, pady=5)

        table_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    window = tk.Tk()
    window.title("Таблицы")
    window.geometry("530x400")
    window.resizable(False, False)

    step_checker = (window.register(validators.natural_positive_number), '%P')

    top_frame = tk.Frame(window)
    top_frame.pack(side="top", fill="x", padx=10, pady=10)

    step_label = tk.Label(top_frame, text="Множитель детализации:", font=("Arial", 10))
    step_label.pack(side="left", padx=(0, 5))

    step_entry = tk.Entry(top_frame, width=10, validate='all', validatecommand=step_checker)
    step_entry.pack(side="left", padx=(0, 5))
    step_entry.insert(0, "5")

    update_button = tk.Button(top_frame, text="Обновить", command=update_tables)
    update_button.pack(side="left")

    canvas = tk.Canvas(window)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    table_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor="nw")

    update_tables(step=5)

    window.mainloop()

