import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
import subprocess

# File paths
CSV_FILE = "programs/exams.csv"
SUBJECTS_FILE = "programs/selected_subjects.csv"
TEST_SCORES_FILE = "programs\study_scores.csv"
DIFFICULTY_FILE = "programs\difficulty.csv"
CHECK_INTERVAL = 1000


# Load per-subject difficulty from prioritized_output.csv if available, else from TEST_SCORES_FILE
def load_difficulties():
    difficulties = {}
    if os.path.exists(DIFFICULTY_FILE):
        try:
            with open(DIFFICULTY_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subj = row.get('subject') or row.get('Subject')
                    diff = row.get('difficulty') or row.get('Difficulty')
                    try:
                        difficulties[subj] = float(diff)
                    except (TypeError, ValueError):
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error loading prioritized difficulties: {e}")
    elif os.path.exists(TEST_SCORES_FILE):
        try:
            with open(TEST_SCORES_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        difficulties[row['subject']] = float(row.get('sac_score_percent', 0))
                    except (TypeError, ValueError):
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error loading test scores: {e}")
    return difficulties

class ExamTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam To-Do List")

        # Load subjects and difficulties
        self.available_subjects = self.load_available_subjects()
        self.test_scores = load_difficulties()
        self.last_modified_time = self.get_prioritized_modified_time()

        self.exams = []
        self.create_input_frame()
        self.create_list_frame()
        self.load_exams_from_csv()
        self.periodic_check()

    def get_prioritized_modified_time(self):
        return os.path.getmtime(DIFFICULTY_FILE) if os.path.exists(DIFFICULTY_FILE) else None

    def load_available_subjects(self):
        subjects = []
        if os.path.exists(SUBJECTS_FILE):
            try:
                with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:  # Only add if row is not empty
                            subjects.extend(row)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading subject file: {e}")
        return sorted(set(subjects))

    def run_subject_selector(self):
        try:
            subprocess.Popen(["python", "Subject_selection.py"])
            messagebox.showinfo("Info", "Subject selector opened. Please return after selecting subjects.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Subject_selection.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running subject selector: {e}")

    def open_testscore_app(self):
        try:
            subprocess.Popen(["python", "testscore.py"])
            messagebox.showinfo("Info", "Test Score app opened.")
        except FileNotFoundError:
            messagebox.showerror("Error", "testscore.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running test score app: {e}")

    def open_subject_difficulty_app(self):
        try:
            subprocess.Popen(["python", "subject_difficulty.py"])
            messagebox.showinfo("Info", "Subject Difficulty app opened.")
        except FileNotFoundError:
            messagebox.showerror("Error", "subject_difficulty.py not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error running subject difficulty app: {e}")

    def periodic_check(self):
        current_mod = self.get_prioritized_modified_time()
        if current_mod and current_mod != self.last_modified_time:
            self.test_scores = load_difficulties()
            self.last_modified_time = current_mod
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Add Exam")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Exam Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Date(YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Subject:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(frame, textvariable=self.subject_var,
                                          values=self.available_subjects, state="readonly")
        self.subject_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        if self.available_subjects:
            self.subject_var.set(self.available_subjects[0])

        self.difficulty_label = ttk.Label(frame, text="Calculated Difficulty: N/A")
        self.difficulty_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=2, rowspan=8, sticky="ns", padx=10)

        ttk.Button(button_frame, text="Add Exam", command=self.add_exam).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Clear All Exams", command=self.clear_exams).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Open Subject Selector", command=self.run_subject_selector).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Start to Study", command=self.start_study).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Open Study Time", command=self.start_studytime).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Open Test Score App", command=self.open_testscore_app).pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Open Subject Difficulty", command=self.open_subject_difficulty_app).pack(fill='x', pady=2)

        self.subject_var.trace_add("write", self.update_difficulty_display)

    def update_difficulty_display(self, *args):
        subject = self.subject_var.get()
        difficulty = self.test_scores.get(subject, None)
        if difficulty is not None:
            self.difficulty_label.config(text=f"Calculated Difficulty: {difficulty:.2f}")
        else:
            self.difficulty_label.config(text="Calculated Difficulty: N/A")

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
        subject = self.subject_var.get()
        difficulty_val = self.test_scores.get(subject, 0.5)

        if not name or not date_str or not subject:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD.")
            return
        exam = {"name": name, "datetime": exam_dt, "difficulty": difficulty_val, "subject": subject}
        self.exams.append(exam)
        self.save_exam_to_csv(exam)
        self.name_var.set("")
        self.date_var.set("")
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
                writer.writerow([exam['name'], exam['datetime'].strftime("%Y-%m-%d"), f"{exam['difficulty']:.2f}", exam['subject']])
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
                            self.exams.append({"name": name, "datetime": exam_dt, "difficulty": float(diff), "subject": subject})
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
            self.tree.insert('', 'end', values=(ex['name'], dt_str, f"{ex['difficulty']:.2f}", ex['subject'], f"{pr:.2f}"))

    def compute_priority(self, exam):
        now = datetime.now()
        delta = (exam['datetime'] - now).total_seconds() / 86400
        return float('inf') if delta <= 0 else exam['difficulty'] / (delta + 1e-9)

def is_subjects_file_empty():
    if not os.path.exists(SUBJECTS_FILE):
        return True
    try:
        with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:  # If any row has content
                    return False
        return True
    except Exception:
        return True

if __name__ == "__main__":
    # Only launch subject selector if selected_subjects.csv is empty or doesn't exist
    if is_subjects_file_empty():
        try:
            subprocess.Popen(["python", "Subject_selection.py"])
            messagebox.showinfo("Info", "Subject selector opened. Close it when done to continue.")
        except Exception as e:
            print(f"Could not open subject selector: {e}")

    root = tk.Tk()
    app = ExamTodoApp(root)
    root.mainloop()