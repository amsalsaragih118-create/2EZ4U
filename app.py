import os
import tkinter as tk

from frontend.ui import Aplikasi


def main():
    root = tk.Tk()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pesanan.csv")
    Aplikasi(root, path)
    root.mainloop()


if __name__ == "__main__":
    main()
