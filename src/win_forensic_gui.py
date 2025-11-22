import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import re
from pathlib import Path
import os

#By Ed Mitchell, and Carson Miller
# ----------------------
# GUI helper functions
# ----------------------

def run_collector():
    """Run the original forensic collector script."""
    try:
        messagebox.showinfo("Running", "Starting forensic collection (may take several minutes)...")
        subprocess.run(["python", "win_forensic_collect.py"], check=True)
        messagebox.showinfo("Done", "Collection complete! Load the new report to view sections.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Collection failed:\n{e}")

def load_report():
    """Load report.txt and split it into sections."""
    file_path = filedialog.askopenfilename(title="Select Forensic Report", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split into sections using the "########" header lines
    sections = re.split(r"(?:#+\n)([A-Z0-9 &/().\-]+)\n#+\n", content)
    # sections[0] = header, then title, content, title, content...

    report_sections.clear()
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        body = sections[i + 1].strip()
        report_sections[title] = body

    update_section_list()

def update_section_list():
    """Populate the section list in the sidebar."""
    section_list.delete(0, tk.END)
    for title in report_sections.keys():
        section_list.insert(tk.END, title)

def show_selected_section(event=None):
    """Display the selected section's content."""
    sel = section_list.curselection()
    if not sel:
        return
    title = section_list.get(sel[0])
    content = report_sections.get(title, "")
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, content)
    section_label.config(text=title)

# ----------------------
# GUI layout
# ----------------------

root = tk.Tk()
root.title("Windows Forensic Report Viewer")
root.geometry("1000x700")

# Toolbar
toolbar = ttk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.X)

ttk.Button(toolbar, text="Run Collection", command=run_collector).pack(side=tk.LEFT, padx=4, pady=4)
ttk.Button(toolbar, text="Load Report", command=load_report).pack(side=tk.LEFT, padx=4, pady=4)

# Split pane
paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

# Left: Section list
left_frame = ttk.Frame(paned, width=250)
section_list = tk.Listbox(left_frame, exportselection=False)
section_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=section_list.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
section_list.config(yscrollcommand=scroll.set)
section_list.bind("<<ListboxSelect>>", show_selected_section)
paned.add(left_frame, weight=1)

# Right: Text display
right_frame = ttk.Frame(paned)
section_label = ttk.Label(right_frame, text="Select a Section", font=("Segoe UI", 12, "bold"))
section_label.pack(anchor="w", padx=5, pady=5)
text_area = tk.Text(right_frame, wrap="word")
text_area.pack(fill=tk.BOTH, expand=True)
scroll_text = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=text_area.yview)
scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
text_area.config(yscrollcommand=scroll_text.set)
paned.add(right_frame, weight=3)

# Storage for parsed sections
report_sections = {}

root.mainloop()

