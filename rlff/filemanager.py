
import tkinter as tk
from tkinter import filedialog


def trajectory_file_manager():
    root = tk.Tk()
    root.withdraw()

    top_path = filedialog.askopenfilename(title='Choose topology file')
    pdb_path = filedialog.askopenfilename(title='Choose structure file')
    return top_path, pdb_path

def sensitivity_file_manager():
    root = tk.Tk()
    root.withdraw()

    top_path = filedialog.askopenfilename(title='Choose topology file')
    pdb_path = filedialog.askopenfilename(title='Choose structure file')
    xtc_path = filedialog.askopenfilename(title='Choose trajectory file')
    dat_path = filedialog.askopenfilename(title='Choose helix file')

    return top_path, pdb_path, xtc_path, dat_path