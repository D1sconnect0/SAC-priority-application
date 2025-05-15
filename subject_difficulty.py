import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

# Paths to CSV files
DIFFICULTY_FILE = os.path.join('programs', 'difficulty.csv')
STUDY_SCORES_FILE = os.path.join('programs', 'study_scores.csv')
SELECTED_SUBJECTS_FILE = os.path.join('programs', 'selected_subjects.csv')
CHECK_INTERVAL = 2000  # milliseconds

def read_csv(filename):
    """
    Read a CSV file and return data as list of rows (including header).
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subject Difficulty Viewer")

        # Track last modification times
        self.diff_mtime = self.get_mtime(DIFFICULTY_FILE)
        self.selected_mtime = self.get_mtime(SELECTED_SUBJECTS_FILE)

        # Create treeview
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both")

        # Initial load of difficulty data
        self.load_difficulty()

        # Start periodic checks
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def get_mtime(self, path):
        return os.path.getmtime(path) if os.path.exists(path) else None

    def load_difficulty(self):
        try:
            data = read_csv(DIFFICULTY_FILE)
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            return
        # Clear existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Populate columns and rows
        headers = data[0]
        self.tree["columns"] = headers
        self.tree["show"] = "headings"
        for col in headers:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        for row in data[1:]:
            if len(row) == len(headers):
                self.tree.insert("", tk.END, values=row)

    def clear_csv(self, path, keep_header=False):
        """Clear CSV file contents, optionally preserving header."""
        try:
            if os.path.exists(path):
                if keep_header:
                    rows = read_csv(path)
                    header = rows[0]
                    with open(path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(header)
                else:
                    open(path, 'w', newline='', encoding='utf-8').close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear '{path}': {e}")

    def periodic_check(self):
        # Check difficulty.csv changes
        new_diff_mtime = self.get_mtime(DIFFICULTY_FILE)
        if new_diff_mtime and new_diff_mtime != self.diff_mtime:
            self.diff_mtime = new_diff_mtime
            self.load_difficulty()

        # Check selected_subjects.csv changes
        new_sel_mtime = self.get_mtime(SELECTED_SUBJECTS_FILE)
        if new_sel_mtime and new_sel_mtime != self.selected_mtime:
            self.selected_mtime = new_sel_mtime
            # Clear both study_scores.csv and difficulty.csv when subjects change
            self.clear_csv(STUDY_SCORES_FILE)
            self.clear_csv(DIFFICULTY_FILE)
            messagebox.showinfo(
                "Info",
                f"Detected change in {SELECTED_SUBJECTS_FILE}; cleared study_scores.csv and difficulty.csv."
            )
            # Clear displayed data
            for item in self.tree.get_children():
                self.tree.delete(item)

        # Schedule next check
        self.root.after(CHECK_INTERVAL, self.periodic_check)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.geometry("600x400")
    root.mainloop()
