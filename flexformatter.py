# -*- coding: utf-8 -*-
"""
MSRC formatter
Main routine
Version 0.1.0
Last update: 2020 - 06 - 25
@author: Nathan Heath Patterson
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, OptionMenu, StringVar
from lxml import etree
import time
import yaml


def format_mis(mis_file, sample_id_str):
    xmltree = etree.parse(mis_file)

    for idx, area in enumerate(xmltree.xpath("Area")):
        area.attrib["Name"] = "{}_roi{}".format(sample_id_str, str(idx).zfill(3))

    return etree.tostring(xmltree, pretty_print=True)


def write_mis(mis_str, file_path):
    with open(file_path, "wb") as f:
        f.write(mis_str)


if __name__ == "__main__":

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    class FlexFormatter(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)

            if getattr(sys, "frozen", False):
                application_path = sys._MEIPASS
            elif __file__:
                application_path = os.path.dirname(__file__)

            self.geometry("700x300+500+500")
            self.title("MSRC - flexImaging 5.0 2D image name formatter")
            icon_file = "msrcicon.ico"
            self.iconbitmap(default=resource_path(icon_file))

            self.iconbitmap("msrcicon.ico")
            self.labels = []
            self.entries = []

            self.mis_button = tk.Button(
                self, text="Select flexImaging .mis sequence", command=self.mis_button
            )
            self.mis_button.grid(row=1, column=0)
            self.template = "BIOMIC"
            self.data_template = {
                "BIOMIC": {
                    "labels": [
                        "Enter HuBMAP ID (VAN0001):",
                        "Enter kidney_side (RK/LK):",
                        "Enter HuBMAP block ID (1):",
                        "Enter HuBMAP sec ID (1):",
                        "Enter local ID (108):",
                        "Select modality (pos/neg):",
                    ],
                    "entries": ["", "", "", "", "", ""],
                    "separators": ["-", "-", "-", "-", "-IMS_"],
                    "input_type": [
                        "text",
                        "text",
                        "numeric",
                        "numeric",
                        "text",
                        "text",
                    ],
                },
                "generic": {
                    "labels": [
                        "Enter Project Name (myproj1):",
                        "Enter sample name (samp01):",
                        "Enter section ID (1):",
                        "Select modality (pos/neg):",
                    ],
                    "entries": ["", "", "", ""],
                    "separators": ["-", "-", "-", "-", "-IMS_"],
                    "input_type": ["text", "text", "numeric", "text",],
                },
            }
            self.template = StringVar("")

            self.dropdown = OptionMenu(
                self,
                self.template,
                *self.data_template.keys(),
                command=self.initialize_ui_from_template
            )

            tk.Label(self, text="Select naming template:").grid(row=2, column=0)
            self.dropdown.grid(row=2, column=1)

            self.initialize_ui_from_template(self.template)

            self.btn_template = tk.Button(
                self, text="load template yaml", command=self.load_template
            )
            self.btn_template.grid(row=2, column=3)

        def initialize_ui_from_template(self, event):

            current_template = self.template.get()
            if current_template == "":
                return

            for grid_item in self.grid_slaves():
                if int(grid_item.grid_info()["row"]) > 2:
                    grid_item.grid_forget()

            self.labels = []
            self.entries = []

            for idx, lbl in enumerate(self.data_template[current_template]["labels"]):
                self.generate_lbl(lbl, idx + 3)
                self.generate_entry(
                    self.data_template[current_template]["entries"][idx], idx + 3
                )
                final_idx = idx + 4

            tk.Label(self, text="").grid(row=final_idx, column=0)

            self.btn_run = tk.Button(
                self, text="Run formatter", command=self.run_button
            )
            self.btn_run.grid(row=final_idx + 1, column=0)

        def generate_lbl(self, lbl_txt, row_pos):
            self.labels.append(tk.Label(self, text=lbl_txt).grid(row=row_pos, column=0))

        def generate_entry(self, default_txt, row_pos):
            entry = tk.Entry(self)
            entry.insert(tk.END, default_txt)
            entry.grid(row=row_pos, column=1)
            self.entries.append(entry)

        def mis_button(self):

            self.file_path_mis = filedialog.askopenfilename(
                title="Select flexImaging .mis seqeuence",
                filetypes=((".mis files", "*.mis"), ("all files", "*.*")),
            )
            tk.Label(self, text=self.file_path_mis).grid(row=1, column=1)

        def load_template(self):

            yaml_fp = filedialog.askopenfilename(
                title="Select .mis naming template .yaml file",
                filetypes=((".yaml files", "*.yaml"), ("all files", "*.*")),
            )

            with open(yaml_fp, "r") as file:
                data_template = yaml.full_load(file)

            data_template["entries"] = ["" for s in data_template["labels"]]

            update_template = {
                data_template["template_name"]: {
                    "labels": data_template["labels"],
                    "entries": data_template["entries"],
                    "input_type": data_template["input_type"],
                    "separators": data_template["separators"],
                }
            }
            self.data_template.update(update_template)

            current_template = self.template.get()
            self.template = StringVar("")
            for grid_item in self.grid_slaves():
                if (
                    int(grid_item.grid_info()["row"]) == 2
                    and int(grid_item.grid_info()["column"]) == 1
                ):
                    grid_item.grid_forget()

            self.dropdown = OptionMenu(
                self,
                self.template,
                *self.data_template.keys(),
                command=self.initialize_ui_from_template
            )

            tk.Label(self, text="Select naming template:").grid(row=2, column=0)
            self.dropdown.grid(row=2, column=1)
            self.template.set(current_template)
            self.initialize_ui_from_template("")

        def format_template_str(self, template):
            def format_number(input_str, input_type):
                if input_type == "numeric":
                    output_str = str(input_str).zfill(3)
                else:
                    output_str = input_str
                return output_str

            time_stamp = datetime.fromtimestamp(time.time()).strftime("%Y%m%d")
            input_strs = [time_stamp, "_"]
            entry_strs = [s.get() for s in self.entries]
            entry_types = self.data_template[template]["input_type"]
            entry_strs_formatted = [
                format_number(s, entry_types[idx]) for idx, s in enumerate(entry_strs)
            ]

            sep_strs = self.data_template[template]["separators"]
            full_str_seq = []
            for idx, input_str in enumerate(entry_strs_formatted):
                if idx < len(entry_strs_formatted) - 1:
                    full_str_seq.append(input_str)
                    full_str_seq.append(sep_strs[idx])
                if idx == len(entry_strs_formatted) - 1:
                    full_str_seq.append(input_str)

            input_strs.extend(full_str_seq)

            file_name_str = "".join(input_strs)
            return file_name_str

        def run_button(self):

            try:
                self.file_path_mis

            except AttributeError:
                messagebox.showerror("Error!", "Please select a .mis file")
                return

            file_name_str = self.format_template_str(self.template.get())
            print(file_name_str)
            formatted_mis = format_mis(self.file_path_mis, file_name_str)
            mis_out = Path(self.file_path_mis).parent / "{}.mis".format(file_name_str)
            write_mis(formatted_mis, str(mis_out))

    w = FlexFormatter()
    w.mainloop()
