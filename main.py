import tkinter as tk
from PreProcessor.Sections import MainWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow.SaprApp(root)
    root.mainloop()
