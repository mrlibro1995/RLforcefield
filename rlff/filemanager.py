
import tkinter as tk
from tkinter import filedialog


def trajectory_file_manager():
    root = tk.Tk()
    root.withdraw()

    top_path = filedialog.askopenfilename(title='Choose topology file')
    pdb_path = filedialog.askopenfilename(title='Choose structure file')
    return top_path, pdb_path