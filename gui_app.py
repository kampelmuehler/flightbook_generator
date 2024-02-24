import sys
import tkinter as tk
from tkinter.filedialog import askdirectory

import sv_ttk

from igc_parser import parse_flights


class StdoutRedirector(object):

    def __init__(self, text_widget: tk.Text):
        """Redirect stdout to a tkinter textbox

        Args:
            text_widget (tk.Text): textbox
        """
        self.textbox = text_widget

    def write(self, string: str):
        """Write a string to the textbox

        Args:
            string (str): string to write
        """
        self.textbox.configure(state='normal')
        self.textbox.insert('end', string)
        self.textbox.see('end')
        self.textbox.configure(state='disabled')

    def flush(self):
        """Flush to avoid delay in output
        """
        self.textbox.update_idletasks()


class Gui(object):

    def __init__(self, parent: tk.Tk) -> None:
        """Build simple gui overlay for igc_parser

        Args:
            parent (tk.Tk): window to add GUI elements to
        """
        self.parent = parent

        self.igc_folder_var = tk.StringVar()
        self.select_igc_folder_label = tk.ttk.Label(self.parent,
                                                    text="No folder selected.")
        self.select_igc_folder_label.grid(row=0, column=1, padx=5, pady=2)
        select_igc_folder_button = tk.ttk.Button(
            self.parent,
            text="Select folder with .igc files",
            command=lambda: self.set_folder(self.igc_folder_var, self.
                                            select_igc_folder_label))
        select_igc_folder_button.grid(row=0, column=0, padx=5, pady=2)

        self.csv_folder_var = tk.StringVar()
        self.select_csv_folder_label = tk.ttk.Label(self.parent,
                                                    text="No folder selected.")
        self.select_csv_folder_label.grid(row=1, column=1, padx=5, pady=2)
        select_csv_folder_button = tk.ttk.Button(
            self.parent,
            text="Select folder to store output in",
            command=lambda: self.set_folder(self.csv_folder_var, self.
                                            select_csv_folder_label))
        select_csv_folder_button.grid(row=1, column=0, padx=5, pady=2)

        select_csv_name_label = tk.ttk.Label(self.parent,
                                             text="Output filename:")
        select_csv_name_label.grid(row=2, column=0, padx=5, pady=2)
        csv_filename_entry = tk.ttk.Entry(self.parent)
        csv_filename_entry.insert(0, "flightbook.csv")
        csv_filename_entry.grid(row=2, column=1, padx=5, pady=2)

        start_button = tk.ttk.Button(
            self.parent,
            text="Start",
            command=lambda: parse_flights(self.igc_folder_var.get(
            ), self.csv_folder_var.get(), csv_filename_entry.get()))
        start_button.grid(row=3, column=0, padx=5, pady=2, columnspan=2)
        self.text_box = tk.Text(self.parent,
                                wrap='word',
                                height=5,
                                width=70,
                                state='disabled')
        self.text_box.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        sys.stdout = StdoutRedirector(self.text_box)
        sv_ttk.set_theme("dark")

    def set_folder(self, folder_path_target: tk.StringVar, label: tk.Label):
        """Set a label to a folder selected by user

        Args:
            folder_path_target (tk.StringVar): target variable for the folder input
            label (tk.Label): the label to set
        """
        if directory := askdirectory():
            folder_path_target.set(str(directory))
        if str(folder_path_target.get()):
            label.config(text=str(folder_path_target.get()))


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Flightbook Generator')
    gui = Gui(root)
    root.mainloop()
