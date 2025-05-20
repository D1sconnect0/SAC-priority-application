import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import csv
import os
import subprocess
from ttkbootstrap import Style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# File paths
CSV_FILE = "programs/exams.csv"
SUBJECTS_FILE = "programs/selected_subjects.csv"
TEST_SCORES_FILE = r"programs/study_scores.csv"
DIFFICULTY_FILE = r"programs/difficulty.csv"
CHECK_INTERVAL = 1000

# Initialize theme
style = Style(theme='minty')

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
        self.root.geometry("1200x800")
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)
        
        # Load data
        self.available_subjects = self.load_available_subjects()
        self.test_scores = load_difficulties()
        self.last_modified_time = self.get_prioritized_modified_time()
        self.exams = []
        
        # Create UI components
        self.create_input_frame()
        self.create_list_frame()
        self.create_visualization_frame()
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
                        if row:
                            subjects.extend(row)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading subject file: {e}")
        return sorted(set(subjects))

    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text=" Add Exam ", bootstyle='info')
        frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Input fields
        ttk.Label(frame, text="Exam Name:", bootstyle='inverse-info').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, bootstyle='info').grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Date (YYYY-MM-DD):", bootstyle='inverse-info').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var, bootstyle='info').grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Subject:", bootstyle='inverse-info').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(
            frame, 
            textvariable=self.subject_var,
            values=self.available_subjects,
            state="readonly",
            bootstyle='info'
        )
        self.subject_combo.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        if self.available_subjects:
            self.subject_var.set(self.available_subjects[0])
        
        self.difficulty_label = ttk.Label(
            frame, 
            text="Calculated Difficulty: N/A", 
            bootstyle='inverse-info'
        )
        self.difficulty_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Button panel
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=2, rowspan=4, padx=10, sticky='ns')
        
        buttons = [
            ("Add Exam", self.add_exam, 'info'),
            ("Clear All", self.clear_exams, 'danger'),
            ("Subject Selector", self.run_subject_selector, 'info'),
            ("Start Studying", self.start_study, 'success'),
            ("Study Time", self.start_studytime, 'info'),
            ("Test Scores", self.open_testscore_app, 'info'),
            ("Subject Difficulty", self.open_subject_difficulty_app, 'info')
        ]
        
        for text, command, btn_style in buttons:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                bootstyle=btn_style,
                width=15
            )
            btn.pack(fill='x', padx=2, pady=2)
        
        self.subject_var.trace_add("write", self.update_difficulty_display)
        frame.columnconfigure(1, weight=1)

    def create_list_frame(self):
        frame = ttk.LabelFrame(self.root, text=" Review Priority ", bootstyle='info')
        frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Treeview setup
        columns = ("name", "datetime", "difficulty", "subject", "priority", "days_left")
        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            bootstyle='info',
            height=12
        )
        
        # Configure columns
        self.tree.heading("name", text="Exam Name")
        self.tree.heading("datetime", text="Date")
        self.tree.heading("difficulty", text="Difficulty")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("days_left", text="Days Left")
        
        self.tree.column("name", width=200, anchor='w')
        self.tree.column("datetime", width=120, anchor='center')
        self.tree.column("difficulty", width=100, anchor='center')
        self.tree.column("subject", width=150, anchor='center')
        self.tree.column("priority", width=100, anchor='center')
        self.tree.column("days_left", width=100, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, bootstyle='info-round', command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, bootstyle='info-round', orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

    def create_visualization_frame(self):
        """Create visualization panel"""
        frame = ttk.LabelFrame(self.root, text=" Data Visualization ", bootstyle='info')
        frame.grid(row=0, column=1, rowspan=2, padx=15, pady=15, sticky="nsew")
        
        # Create notebook
        notebook = ttk.Notebook(frame, bootstyle='info')
        notebook.pack(fill='both', expand=True)
        
        # Priority distribution pie chart
        pie_frame = ttk.Frame(notebook)
        self.pie_fig, self.pie_ax = plt.subplots(figsize=(6, 5), dpi=80)
        self.pie_fig.patch.set_facecolor('#4a4a4a')
        self.pie_ax.set_facecolor('#4a4a4a')
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, pie_frame)
        self.pie_canvas.get_tk_widget().pack(fill='both', expand=True)
        notebook.add(pie_frame, text="Priority Distribution")
        
        # Exam timeline
        timeline_frame = ttk.Frame(notebook)
        self.timeline_fig, self.timeline_ax = plt.subplots(figsize=(6, 5), dpi=80)
        self.timeline_fig.patch.set_facecolor('#4a4a4a')
        self.timeline_ax.set_facecolor('#4a4a4a')
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, timeline_frame)
        self.timeline_canvas.get_tk_widget().pack(fill='both', expand=True)
        notebook.add(timeline_frame, text="Exam Timeline")
        
        # Difficulty progress bars
        progress_frame = ttk.Frame(notebook)
        self.difficulty_bars = {}
        for subj in self.available_subjects:
            bar_frame = ttk.Frame(progress_frame)
            bar_frame.pack(fill='x', pady=3)
            
            ttk.Label(bar_frame, text=subj[:15], width=15).pack(side='left')
            bar = ttk.Progressbar(
                bar_frame, 
                orient='horizontal',
                length=200,
                mode='determinate',
                bootstyle='info-striped'
            )
            bar.pack(side='left', expand=True, fill='x')
            self.difficulty_bars[subj] = bar
        notebook.add(progress_frame, text="Subject Difficulty")
        
        self.update_visualizations()

    def update_visualizations(self):
        """Update all visualizations"""
        # Update pie chart
        self.pie_ax.clear()
        if self.exams:
            priorities = [self.compute_priority(e) for e in self.exams]
            labels = [e['name'] for e in self.exams]
            colors = plt.cm.Paired.colors[:len(priorities)]
            
            wedges, texts, autotexts = self.pie_ax.pie(
                priorities,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'color': 'white'}
            )
            self.pie_ax.axis('equal')
            self.pie_canvas.draw()
        
        # Update timeline
        self.timeline_ax.clear()
        if self.exams:
            dates = [e['datetime'] for e in self.exams]
            names = [e['name'] for e in self.exams]
            colors = ['#e74c3c' if (e['datetime'] - datetime.now()).days <= 3 
                     else '#f1c40f' if (e['datetime'] - datetime.now()).days <= 7 
                     else '#2ecc71' for e in self.exams]
            
            self.timeline_ax.barh(
                names,
                [1] * len(names),
                left=[datetime.now()] * len(names),
                color=colors,
                height=0.5
            )
            self.timeline_ax.set_xlim(datetime.now(), max(dates) + timedelta(days=1))
            self.timeline_ax.xaxis_date()
            self.timeline_ax.tick_params(axis='both', colors='white')
            self.timeline_fig.autofmt_xdate()
            self.timeline_canvas.draw()
        
        # Update difficulty bars
        for subj, bar in self.difficulty_bars.items():
            diff = self.test_scores.get(subj, 0)
            bar['value'] = diff * 100
            style = 'danger' if diff > 0.7 else 'warning' if diff > 0.4 else 'success'
            bar.configure(bootstyle=(style, 'striped'))

    def update_difficulty_display(self, *args):
        subject = self.subject_var.get()
        difficulty = self.test_scores.get(subject, None)
        if difficulty is not None:
            self.difficulty_label.config(text=f"Calculated Difficulty: {difficulty:.2f}")
        else:
            self.difficulty_label.config(text="Calculated Difficulty: N/A")

    def add_exam(self):
        name = self.name_var.get().strip()
        date_str = self.date_var.get().strip()
        subject = self.subject_var.get()
        difficulty_val = self.test_scores.get(subject, 0.5)

        if not name or not date_str or not subject:
            messagebox.showwarning("Input Error", "Please fill in all fields.", parent=self.root)
            return
        try:
            exam_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Error", "Date format should be YYYY-MM-DD.", parent=self.root)
            return
        
        exam = {"name": name, "datetime": exam_dt, "difficulty": difficulty_val, "subject": subject}
        self.exams.append(exam)
        self.save_exam_to_csv(exam)
        self.name_var.set("")
        self.date_var.set("")
        self.subject_var.set(self.available_subjects[0] if self.available_subjects else "")
        self.show_priority()
        self.update_visualizations()
        messagebox.showinfo("Success", f"Exam '{name}' added.", parent=self.root)

    def save_exam_to_csv(self, exam):
        try:
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    exam['name'],
                    exam['datetime'].strftime("%Y-%m-%d"),
                    f"{exam['difficulty']:.2f}",
                    exam['subject']
                ])
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving exam: {e}", parent=self.root)

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
                            self.exams.append({
                                "name": name,
                                "datetime": exam_dt,
                                "difficulty": float(diff),
                                "subject": subject
                            })
                        except ValueError:
                            continue
            self.show_priority()
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading exams: {e}", parent=self.root)

    def clear_exams(self):
        if messagebox.askyesno("Confirm", "Delete all exams?", parent=self.root):
            self.exams.clear()
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                    pass
            self.show_priority()
            self.update_visualizations()

    def show_priority(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Configure tags
        self.tree.tag_configure('high', background='#e74c3c', foreground='white')
        self.tree.tag_configure('medium', background='#f1c40f')
        self.tree.tag_configure('low', background='#2ecc71')
        
        prioritized = sorted(self.exams, key=lambda e: self.compute_priority(e), reverse=True)
        for ex in prioritized:
            pr = self.compute_priority(ex)
            days_left = (ex['datetime'] - datetime.now()).days
            dt_str = ex['datetime'].strftime("%d-%m-%Y")
            
            # Determine tag
            if days_left <= 0:
                tags = ('high',)
            elif days_left <= 3:
                tags = ('high',)
            elif days_left <= 7:
                tags = ('medium',)
            else:
                tags = ('low',)
            
            self.tree.insert('', 'end', 
                values=(
                    ex['name'],
                    dt_str,
                    f"{ex['difficulty']:.2f}",
                    ex['subject'],
                    f"{pr:.2f}",
                    f"{days_left} days"
                ),
                tags=tags
            )
        
        self.update_visualizations()

    def compute_priority(self, exam):
        now = datetime.now()
        delta = (exam['datetime'] - now).total_seconds() / 86400
        return float('inf') if delta <= 0 else exam['difficulty'] / (delta + 1e-9)

    def periodic_check(self):
        current_mod = self.get_prioritized_modified_time()
        if current_mod and current_mod != self.last_modified_time:
            self.test_scores = load_difficulties()
            self.last_modified_time = current_mod
        self.root.after(CHECK_INTERVAL, self.periodic_check)

    def run_subject_selector(self):
        try:
            subprocess.Popen(["python", "Subject_selection.py"])
            messagebox.showinfo("Info", "Subject selector opened.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def start_study(self):
        try:
            subprocess.Popen(["python", "clockapp.py"])
            messagebox.showinfo("Info", "Study timer started.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def start_studytime(self):
        try:
            subprocess.Popen(["python", "studytime.py"])
            messagebox.showinfo("Info", "Study time tracker opened.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def open_testscore_app(self):
        try:
            subprocess.Popen(["python", "testscore.py"])
            messagebox.showinfo("Info", "Test score app opened.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def open_subject_difficulty_app(self):
        try:
            subprocess.Popen(["python", "subject_difficulty.py"])
            messagebox.showinfo("Info", "Subject difficulty app opened.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

def is_subjects_file_empty():
    if not os.path.exists(SUBJECTS_FILE):
        return True
    try:
        with open(SUBJECTS_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    return False
        return True
    except Exception:
        return True

if __name__ == "__main__":
    if is_subjects_file_empty():
        try:
            subprocess.Popen(["python", "Subject_selection.py"])
            messagebox.showinfo("Info", "Please select subjects first.")
        except Exception as e:
            print(f"Error: {e}")

    root = style.master
    app = ExamTodoApp(root)
    root.mainloop()