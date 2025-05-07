import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
import shutil
import subprocess
import time

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
        ttk.style.theme_use('clam')  # You can try other themes like 'alt', 'default', 'classic'

        self.exams = []
        self.available_subjects = self.load_available_subjects()
        self.last_modified_time = self.get_subjects_file_modified_time()

        self.create_input_frame()
        self.create_list_frame()
        self.load_exams_from_csv()
        self.periodic_check()

        # self.test_calendar_output() # Uncomment to run the test function

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
        return sorted(list(set(subjects))) # Remove duplicates and sort

    def run_subject_selector(self):
        try:
            subprocess.Popen(["python", "Subject selection.py"])
            messagebox.showinfo("Info", "Subject selector opened. Please return to this application after making your selections.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Subject selection.py file not found. Please ensure the file is in the correct path.")
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
        if current_modified_time is not None and current_modified_time != self.last_modified_time:
            self.update_available_subjects()
            self.last_modified_time = current_modified_time
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    # def show_calendar(self):
    #     top = tk.Toplevel(self.root)
    #     top.title("Choose Date")
    #     cal = Calendar(top, font="Arial 12", selectmode='day',
    #                    cursor="hand1")
    #     cal.grid(row=0, column=0, padx=10, pady=10)
    #
    #     def print_and_set():
    #         selected_date = cal.get_date()
    #         print(f"Date from cal.get_date(): {selected_date}") # VERY IMPORTANT: What does this print?
    #         self.set_date(selected_date, top)
    #
    #     ttk.Button(top, text="Select Date", command=print_and_set).grid(row=1, column=0, pady=5)

    # def set_date(self, selected_date, top_window):
    #     try:
    #         # Parse the date from tkcalendar (mm/dd/yyyy)
    #         date_object = datetime.strptime(selected_date, "%m/%d/%Y")
    #         # Format it to the desired CANVAS-MM-DD for internal use
    #         formatted_date = date_object.strftime("%Y-%m-%d")
    #         self.date_var.set(formatted_date)
    #         top_window.destroy()
    #     except ValueError as e:
    #         # This error is unlikely with tkcalendar's standard output
    #         messagebox.showerror("Date Error", f"Unexpected date format from calendar: {selected_date}. Error: {e}")

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Add Exam") # More user-friendly label
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Exam Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5) # Add padding
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=self.name_var)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        name_entry.focus() # Default focus on the name entry

        ttk.Label(frame, text="Date(YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(frame, textvariable=self.date_var) # Allow manual input
        date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        # The "Choose Date" button is removed
        # ttk.Button(frame, text="Choose Date", command=self.show_calendar).grid(row=1, column=2, padx=5, pady=5) # More user-friendly button text

        ttk.Label(frame, text="Difficulty:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.diff_var = tk.StringVar(value="Medium")
        self.diff_combo = ttk.Combobox(frame, textvariable=self.diff_var, values=["Low", "Medium", "High"], state="readonly")
        self.diff_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="Subject:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(frame, textvariable=self.subject_var, values=self.available_subjects, state="readonly")
        self.subject_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        if self.available_subjects:
            self.subject_var.set(self.available_subjects[0])

        add_btn = ttk.Button(frame, text="Add Exam", command=self.add_exam) # More user-friendly button text
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)

        clear_btn = ttk.Button(frame, text="Clear All Exams", command=self.clear_exams) # More user-friendly button text
        clear_btn.grid(row=5, column=0, columnspan=2, pady=5)

        subject_selector_btn = ttk.Button(frame, text="Open Subject Selector", command=self.run_subject_selector) # More user-friendly button text
        subject_selector_btn.grid(row=6, column=0, columnspan=2, pady=5)

        frame.columnconfigure(1, weight=1)
        # frame.columnconfigure(2, weight=0) # This column is now gone

    def create_list_frame(self):
        frame = ttk.LabelFrame(self.root, text="Review Order") # More user-friendly label
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        cols = ("name", "datetime", "difficulty", "subject", "priority")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            heading_text = {"name": "Exam Name", "datetime": "Date", "difficulty": "Difficulty", "subject": "Subject", "priority": "Priority"}.get(col, col.title()) # More user-friendly column headings
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, width=100, stretch=tk.YES) # Set initial column width and stretchability
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
        subject = self.subject_var.get()
        if not name or not date_str or not subject:
            messagebox.showwarning("Input Error", "Please fill in all fields.") # More user-friendly message
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD.") # More user-friendly message
            return
        exam = {"name": name, "datetime": exam_dt, "difficulty": diff, "subject": subject}
        self.exams.append(exam)
        self.save_exam_to_csv(exam)
        self.name_var.set("")
        self.date_var.set("")
        self.diff_var.set("Medium")
        self.subject_var.set(self.available_subjects[0] if self.available_subjects else "")
        self.show_priority()
        messagebox.showinfo("Success", f"Exam '{name}' successfully added to the list.") # Success message

    def difficulty_score(self, level):
        return {"Low": 1, "Medium": 2, "High": 3}.get(level, 1)

    def compute_priority(self, exam):
        now = datetime.now()
        delta = (exam["datetime"] - now).total_seconds() / 86400
        if delta <= 0:
            return float('inf')
        return self.difficulty_score(exam["difficulty"]) / (delta + 1e-9) # Avoid division by zero

    def show_priority(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        prioritized = sorted(self.exams, key=lambda e: self.compute_priority(e), reverse=True)
        for ex in prioritized:
            pr = self.compute_priority(ex)
            # Format the date for display as dd-mm-yyyy
            dt_str = ex["datetime"].strftime("%d-%m-%Y")
            self.tree.insert('', 'end', values=(ex["name"], dt_str, ex["difficulty"], ex["subject"], f"{pr:.2f}"))

    def save_exam_to_csv(self, exam):
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([exam["name"], exam["datetime"].strftime("%Y-%m-%d"), exam["difficulty"], exam["subject"]])
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving exam information to CSV file: {e}")

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
                    elif len(row) == 3: # Handle old files without subject
                        name, date_str, diff = row
                        try:
                            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
                            self.exams.append({"name": name, "datetime": exam_dt, "difficulty": diff, "subject": ""})
                        except ValueError:
                            continue
            self.show_priority()
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading exam information: {e}")

    def clear_exams(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all exams?"): # More user-friendly message
            self.exams.clear()
            if os.path.exists(CSV_FILE):
                try:
                    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                        pass
                    messagebox.showinfo("Success", "All exams cleared.") # Success message
                except Exception as e:
                    messagebox.showerror("Error", f"Error clearing exam file: {e}")
            self.show_priority()

    def test_calendar_output(self):
        top = tk.Toplevel(self.root)
        cal = Calendar(top)
        date_label = ttk.Label(top, text="")

        def show_selected():
            date_label.config(text=cal.get_date())

        ttk.Button(top, text="Get Date", command=show_selected).pack(pady=10)
        date_label.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamTodoApp(root)
    root.mainloop()