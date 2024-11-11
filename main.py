import tkinter as tk
from PreProcessor import main_app


if __name__ == "__main__":
    root = tk.Tk()
    app = main_app.SaprApp(root)
    root.mainloop()
