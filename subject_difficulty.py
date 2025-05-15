import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

# Path to the difficulty CSV
DIFFICULTY_FILE = os.path.join('programs', 'difficulty.csv')
CHECK_INTERVAL = 2000  # milliseconds to check for header change

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

        # Load initial CSV data
        try:
            data = read_csv(DIFFICULTY_FILE)
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            data = []

        # Store initial headers
        self.headers = data[0] if data else []

        # Create treeview widget
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both")

        # Populate if data exists
        if self.headers:
            self.tree["columns"] = self.headers
            self.tree["show"] = "headings"
            for col in self.headers:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor='center')
            for row in data[1:]:
                if len(row) == len(self.headers):
                    self.tree.insert("", tk.END, values=row)

        # Start periodic check for header changes
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def periodic_check(self):
        # Check for header change
        try:
            data = read_csv(DIFFICULTY_FILE)
        except FileNotFoundError:
            self.root.after(CHECK_INTERVAL, self.periodic_check)
            return
        new_headers = data[0] if data else []
        # If headers changed (e.g., Subject column renamed)
        if new_headers and new_headers != self.headers:
            # Clear all displayed rows (scores)
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Info", "CSV headers changed; all scores cleared.")
            # Update treeview columns to new headers
            self.headers = new_headers
            self.tree["columns"] = self.headers
            for col in self.headers:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor='center')
        # Schedule next check
        self.root.after(CHECK_INTERVAL, self.periodic_check)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.geometry("600x400")
    root.mainloop()