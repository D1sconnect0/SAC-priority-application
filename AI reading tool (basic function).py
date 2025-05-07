import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ExamTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam To-Do List")
        self.exams = []  # list of dicts with keys: name, datetime, difficulty

        self.create_input_frame()
        self.create_list_frame()

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Add Exam")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Exam Name:").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="Date & Time (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w")
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var).grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Difficulty:").grid(row=2, column=0, sticky="w")
        self.diff_var = tk.StringVar(value="Medium")
        self.diff_combo = ttk.Combobox(frame, textvariable=self.diff_var, values=["Low", "Medium", "High"], state="readonly")
        self.diff_combo.grid(row=2, column=1, sticky="ew")

        add_btn = ttk.Button(frame, text="Add Exam", command=self.add_exam)
        add_btn.grid(row=3, column=0, columnspan=2, pady=5)

        frame.columnconfigure(1, weight=1)

    def create_list_frame(self):
        frame = ttk.LabelFrame(self.root, text="Review Order")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        cols = ("name", "datetime", "difficulty", "priority")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col.title())
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def add_exam(self):
        name = self.name_var.get().strip()
        date_str = self.date_var.get().strip()
        diff = self.diff_var.get()
        if not name or not date_str:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD HH:MM")
            return
        self.exams.append({"name": name, "datetime": exam_dt, "difficulty": diff})
        messagebox.showinfo("Added", f"Exam '{name}' added.")
        self.name_var.set("")
        self.date_var.set("")
        self.diff_var.set("Medium")
        self.show_priority()  # Automatically update priority list

    def difficulty_score(self, level):
        return {"Low": 1, "Medium": 2, "High": 3}.get(level, 1)

    def compute_priority(self, exam):
        # priority score: difficulty_score / days until exam
        now = datetime.now()
        delta = (exam["datetime"] - now).total_seconds() / 86400  # days
        if delta <= 0:
            return float('inf')
        return self.difficulty_score(exam["difficulty"]) / delta

    def show_priority(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        prioritized = sorted(self.exams, key=lambda e: self.compute_priority(e), reverse=True)
        for ex in prioritized:
            pr = self.compute_priority(ex)
            dt_str = ex["datetime"].strftime("%Y-%m-%d %H:%M")
            self.tree.insert('', 'end', values=(ex["name"], dt_str, ex["difficulty"], f"{pr:.2f}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamTodoApp(root)
    root.mainloop()
