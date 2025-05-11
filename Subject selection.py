import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
import subprocess

CSV_FILE = "programs/exams.csv"
BACKUP_FILE = "programs/exams_backup.csv"
SUBJECTS_FILE = "programs/selected_subjects.csv"
CHECK_INTERVAL = 1000

class ExamTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam To-Do List")

        # Set ttk theme
        ttk.style = ttk.Style(root)
        ttk.style.theme_use('clam')

        self.exams = []
        self.available_subjects = self.load_available_subjects()
        self.last_modified_time = self.get_subjects_file_modified_time()

        self.create_input_frame()
        self.create_list_frame()
        self.load_exams_from_csv()
        self.periodic_check()

    def get_subjects_file_modified_time(self):
        if os.path.exists(SUBJECTS_FILE):
            return os.path.getmtime(SUBJECTS_FILE)
        return None

    def load_available_subjects(self):
        subjects = []
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        subjects.extend(row)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading subject file: {e}")
        return sorted(set(subjects))

    def run_subject_selector(self):
        try:
            subprocess.Popen(["python", "Subject selection.py"])
            messagebox.showinfo("Info", "Subject selector opened. Please return after selecting subjects.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Subject selection.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running subject selector: {e}")

    def update_available_subjects(self):
        new_subjects = self.load_available_subjects()
        if new_subjects != self.available_subjects:
            self.available_subjects = new_subjects
            self.subject_combo['values'] = self.available_subjects
            if self.available_subjects and self.subject_var.get() not in self.available_subjects:
                self.subject_var.set(self.available_subjects[0])

    def periodic_check(self):
        current_modified_time = self.get_subjects_file_modified_time()
        if current_modified_time and current_modified_time != self.last_modified_time:
            self.update_available_subjects()
            self.last_modified_time = current_modified_time
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Add Exam")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Exam Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Date(YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Difficulty:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.diff_var = tk.StringVar(value="Medium")
        ttk.Combobox(frame, textvariable=self.diff_var,
                     values=["Low", "Medium", "High"], state="readonly").grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Subject:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(frame, textvariable=self.subject_var,
                                          values=self.available_subjects, state="readonly")
        self.subject_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        if self.available_subjects:
            self.subject_var.set(self.available_subjects[0])

        # Make add exam larger by weighting column 0 heavier
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)

        # Add Exam (larger) and Clear All Exams side by side
        ttk.Button(frame, text="Add Exam", command=self.add_exam).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(frame, text="Clear All Exams", command=self.clear_exams).grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Subject selector below spanning both columns
        ttk.Button(frame, text="Open Subject Selector",
                   command=self.run_subject_selector).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        # Study buttons side by side with start larger
        # (column weights already set)
        ttk.Button(frame, text="Start to Study", command=self.start_study).grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(frame, text="Open Study Time", command=self.start_studytime).grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    def create_list_frame(self):
        frame = ttk.LabelFrame(self.root, text="Review Order")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        cols = ("name", "datetime", "difficulty", "subject", "priority")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=100, stretch=tk.YES)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, command=self.tree.yview, orient=tk.VERTICAL)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def add_exam(self):
        name = self.name_var.get().strip()
        date_str = self.date_var.get().strip()
        diff = self.diff_var.get()
        subject = self.subject_var.get()
        if not name or not date_str or not subject:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD.")
            return
        exam = {"name": name, "datetime": exam_dt, "difficulty": diff, "subject": subject}
        self.exams.append(exam)
        self.save_exam_to_csv(exam)
        self.name_var.set("")
        self.date_var.set("")
        self.diff_var.set("Medium")
        self.subject_var.set(self.available_subjects[0] if self.available_subjects else "")
        self.show_priority()
        messagebox.showinfo("Success", f"Exam '{name}' added.")

    def start_study(self):
        try:
            subprocess.Popen(["python", "clockapp.py"])
            messagebox.showinfo("Info", "Clock app opened for study time.")
        except FileNotFoundError:
            messagebox.showerror("Error", "clockapp.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running clock app: {e}")

    def start_studytime(self):
        try:
            subprocess.Popen(["python", "studytime.py"])
            messagebox.showinfo("Info", "Study Time app opened.")
        except FileNotFoundError:
            messagebox.showerror("Error", "studytime.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running Study Time app: {e}")

    def save_exam_to_csv(self, exam):
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([exam['name'], exam['datetime'].strftime("%Y-%m-%d"), exam['difficulty'], exam['subject']])
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving exam: {e}")

    def load_exams_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 4:
                        name, date_str, diff, subject = row
                        try:
                            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
                            self.exams.append({"name": name, "datetime": exam_dt, "difficulty": diff, "subject": subject})
                        except ValueError:
                            continue
            self.show_priority()
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading exams: {e}")

    def clear_exams(self):
        if messagebox.askyesno("Confirm", "Delete all exams?"):
            self.exams.clear()
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                    pass
            self.show_priority()

    def show_priority(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        prioritized = sorted(self.exams, key=lambda e: self.compute_priority(e), reverse=True)
        for ex in prioritized:
            pr = self.compute_priority(ex)
            dt_str = ex['datetime'].strftime("%d-%m-%Y")
            self.tree.insert('', 'end', values=(ex['name'], dt_str, ex['difficulty'], ex['subject'], f"{pr:.2f}"))

    def compute_priority(self, exam):
        now = datetime.now()
        delta = (exam['datetime'] - now).total_seconds() / 86400
        return float('inf') if delta <= 0 else self.difficulty_score(exam['difficulty']) / (delta + 1e-9)

    def difficulty_score(self, level):
        return {"Low": 1, "Medium": 2, "High": 3}.get(level, 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamTodoApp(root)
    root.mainloop()
